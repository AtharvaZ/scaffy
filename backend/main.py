from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pyd_models.schemas import (
    AssignmentSchema,
    TaskBreakdownSchema,
    BoilerPlateCodeSchema,
    StarterCode,
    HintResponseSchema,
    HintSchema,
    CodeExecutionRequest,
    CodeExecutionResult,
    PDFExtractionResult,
    ConceptExampleRequest,
    ConceptExampleResponse
)

# Import agents and services
from agents.parser_agent import ParserAgent
from agents.codegen_agent import CodegenAgent
from agents.live_helper import LiveHelperAgent
from agents.concept_example import ConceptExampleAgent
from services.code_runner import get_code_runner
from services.pdf_extractor import get_pdf_extractor

load_dotenv()

app = FastAPI(
    title="Scaffy Backend",
    description="AI-powered tool that breaks down programming assignments into manageable tasks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser_agent = ParserAgent()
codegen_agent = CodegenAgent()
helper_agent = LiveHelperAgent()
concept_example_agent = ConceptExampleAgent()

@app.get("/")
async def root():
    """Simple health check"""
    return {
        "message": "Assignment Scaffolder API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents": {
            "parser": "ready",
            "codegen": "ready",
            "helper": "ready"
        },
        "api_key_set": bool(os.getenv("ANTHROPIC_API_KEY"))
    }


# ============================================
# AGENT 1: ASSIGNMENT PARSER
# ============================================

@app.post("/parse-assignment", response_model=TaskBreakdownSchema)
async def parse_assignment(assignment: AssignmentSchema):
    """
    Break down an assignment into ordered tasks with dependencies
    
    Agent 1 analyzes the assignment and creates a structured breakdown.
    """
    try:
        # Log the received assignment for debugging
        logger.info("=" * 80)
        logger.info("RECEIVED ASSIGNMENT REQUEST:")
        logger.info(f"Assignment Text: {assignment.assignment_text[:200]}..." if len(assignment.assignment_text) > 200 else f"Assignment Text: {assignment.assignment_text}")
        logger.info(f"Target Language: {assignment.target_language}")
        logger.info(f"Known Language: {assignment.known_language}")
        logger.info(f"Experience Level: {assignment.experience_level}")
        logger.info("=" * 80)
        
        # Call Agent 1 to parse the assignment
        result = parser_agent.parse_assignment(assignment)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse assignment: {str(e)}"
        )


# ============================================
# AGENT 2: STARTER CODE GENERATOR
# ============================================

@app.post("/generate-starter-code", response_model=StarterCode)
async def generate_starter_code(request: BoilerPlateCodeSchema):
    """
    Generate starter code template with TODOs for a specific task
    
    Agent 2 creates code templates with intelligent concept examples
    based on the student's known language.
    """
    try:
        # Call Agent 2 to generate starter code
        result = codegen_agent.generate_boilerplate_code(request)
        return result
    
    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"Failed to generate starter code: {e}", exc_info=True)
        
        # Provide user-friendly error messages for API errors
        if "rate limit" in error_str or "overloaded" in error_str or "529" in error_str or "temporarily unavailable" in error_str:
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail="The AI service is temporarily overloaded. Please try again in a few moments. If the issue persists, wait a bit longer and try again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate starter code: {str(e)}"
            )


# ============================================
# AGENT 3: LIVE CODING HELPER
# ============================================

@app.post("/get-hint", response_model=HintSchema)
async def get_hint(request: HintResponseSchema):
    """
    Get a contextual hint when student is stuck
    
    Agent 3 provides progressive hints based on how many times
    the student has asked for help on this task.
    
    Hint levels:
    - 1st request: Gentle, conceptual guidance
    - 2nd request: More specific with examples
    - 3rd+ request: Detailed hint close to solution
    """
    try:
        # Call Agent 3 to get a hint
        result = helper_agent.provide_hint(request)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate hint: {str(e)}"
        )

# ============================================
# ON-DEMAND CONCEPT EXAMPLES
# ============================================

@app.post("/get-concept-example", response_model=ConceptExampleResponse)
async def get_concept_example(request: ConceptExampleRequest):
    
    try:
        logger.info(f"Generating on-demand example for concept: {request.concept} in {request.programming_language}")
        
        # Call the concept example agent
        result = concept_example_agent.generate_example(request)
        
        logger.info(f"Successfully generated {result.example_type} example for {request.concept}")
        return result
    
    except Exception as e:
        logger.error(f"Failed to generate concept example: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate concept example: {str(e)}"
        )

# ============================================
# CODE EXECUTION
# ============================================

@app.post("/run-code", response_model=CodeExecutionResult)
async def run_code(request: CodeExecutionRequest):
    """
    Execute student code and return results
    
    Supports Python and JavaScript execution with:
    - 5 second timeout
    - Output capture
    - Error handling
    """
    try:
        logger.info(f"Executing {request.language} code ({len(request.code)} characters)")
        
        code_runner = get_code_runner()
        # Pass stdin if provided, otherwise use default test values
        result = code_runner.run_code(request.code, request.language, stdin=request.stdin)
        
        logger.info(f"Execution completed: success={result['success']}, exit_code={result['exit_code']}")
        
        return CodeExecutionResult(**result)
    
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute code: {str(e)}"
        )


# ============================================
# PDF TEXT EXTRACTION
# ============================================

@app.post("/extract-pdf-text", response_model=PDFExtractionResult)
async def extract_pdf_text(file: UploadFile = File(...)):
    """
    Extract text from uploaded PDF file
    
    Supports PDF text extraction with:
    - File validation (PDF only, max 10MB)
    - Multi-page extraction
    - Error handling for corrupted/invalid PDFs
    """
    try:
        logger.info(f"Received PDF upload request: {file.filename} ({file.content_type})")
        
        pdf_extractor = get_pdf_extractor()
        result = await pdf_extractor.extract_text(file)
        
        if result['success']:
            logger.info(f"Successfully extracted text from PDF: {result['page_count']} pages, {len(result['extracted_text'])} characters")
        else:
            logger.warning(f"PDF extraction failed: {result['error']}")
        
        return PDFExtractionResult(**result)
    
    except Exception as e:
        logger.error(f"PDF extraction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


# ============================================
# ON-DEMAND CONCEPT EXAMPLES
# ============================================

@app.post("/get-concept-example", response_model=ConceptExampleResponse)
async def get_concept_example(request: ConceptExampleRequest):
    """
    Generate on-demand concept examples for students
    
    Provides examples of programming concepts in the student's known language
    to help them understand and apply concepts to the target language.
    """
    try:
        logger.info(f"Generating on-demand example for concept: {request.concept} in {request.programming_language}")
        
        # Call the concept example agent
        result = concept_example_agent.generate_example(request)
        
        logger.info(f"Successfully generated {result.example_type} example for {request.concept}")
        return result
    
    except Exception as e:
        logger.error(f"Failed to generate concept example: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate concept example: {str(e)}"
        )


# ============================================
# RUN THE APP
# ============================================

if __name__ == "__main__":
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )