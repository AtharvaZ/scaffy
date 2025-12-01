from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import security utilities
from utils.security import (
    validate_assignment_text,
    validate_code,
    validate_hint_question,
    validate_pdf_file,
    validate_language,
    validate_request_size,
    check_malicious_content,
    sanitize_filename
)
from config import MAX_PDF_SIZE, MAX_TOTAL_FILES_SIZE

from pyd_models.schemas import (
    AssignmentSchema,
    TaskBreakdownSchema,
    HintResponseSchema,
    HintSchema,
    CodeExecutionRequest,
    CodeExecutionResult,
    PDFExtractionResult,
    ConceptExampleRequest,
    ConceptExampleResponse,
    BatchBoilerPlateCodeSchema,
    BatchStarterCodeResponse,
    GenerateTestsRequest,
    GenerateTestsResponse,
    FeedbackRequest,
    FeedbackResponse
)

# Import agents and services
from agents.parser_agent import ParserAgent
from agents.codegen_agent import CodegenAgent
from agents.live_helper import LiveHelperAgent
from agents.concept_example import ConceptExampleAgent
from services.code_runner import get_code_runner
from services.pdf_extractor import get_pdf_extractor
from services.resend_email_service import get_resend_email_service

load_dotenv()

app = FastAPI(
    title="Scaffy Backend",
    description="AI-powered tool that breaks down programming assignments into manageable tasks",
    version="1.0.0"
)

# Import and add rate limiting middleware
from middleware.rate_limiter import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://scaffi-ai.onrender.com", 
        "http://localhost:5173",  # Local dev
        "http://localhost:3000" ],
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
@app.head("/health")
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

@app.post("/generate-starter-code-batch", response_model=BatchStarterCodeResponse)
async def generate_starter_code_bacth(request: BatchBoilerPlateCodeSchema):
    """
    Generate starter code - now processes files separately for better quality
    """
    try:
        import time
        start_time = time.time()

        logger.info("=" * 80)
        logger.info("BATCH CODE GENERATION REQUEST")
        logger.info(f"Number of tasks: {len(request.tasks)}")

        # Group tasks by filename and track class structure
        files_map = {}

        for task in request.tasks:
            filename = task.filename
            class_name = getattr(task, 'class_name', None)

            if filename not in files_map:
                files_map[filename] = {
                    'tasks': [],
                    'class_structure': {},
                    'template_variables': set(),
                    'method_signatures_by_class': {}  # Track methods per class
                }

            # Add task to file
            files_map[filename]['tasks'].append(task)

            # Track template variables
            if hasattr(task, 'template_variables') and task.template_variables:
                files_map[filename]['template_variables'].update(task.template_variables)

            # Track method signatures per class
            if hasattr(task, 'method_signatures') and task.method_signatures and class_name:
                if class_name not in files_map[filename]['method_signatures_by_class']:
                    files_map[filename]['method_signatures_by_class'][class_name] = set()
                files_map[filename]['method_signatures_by_class'][class_name].update(task.method_signatures)

            # Track class membership
            if class_name:
                if class_name not in files_map[filename]['class_structure']:
                    files_map[filename]['class_structure'][class_name] = []
                files_map[filename]['class_structure'][class_name].append(task)

        logger.info(f"Tasks organized into {len(files_map)} files")
        for filename, file_data in files_map.items():
            logger.info(f"  - {filename}: {len(file_data['tasks'])} tasks")
            if file_data['class_structure']:
                logger.info(f"    Classes: {', '.join(file_data['class_structure'].keys())}")

        # Validate class-task distribution before generation
        for filename, file_data in files_map.items():
            class_structure = file_data['class_structure']
            if class_structure:
                # Check for imbalanced distribution
                tasks_per_class = {cls: len(tasks) for cls, tasks in class_structure.items()}
                max_tasks = max(tasks_per_class.values())
                min_tasks = min(tasks_per_class.values())

                if max_tasks > min_tasks * 3:
                    logger.warning(f"⚠️  {filename}: Imbalanced task distribution across classes")
                    for cls, count in tasks_per_class.items():
                        logger.warning(f"    {cls}: {count} tasks")

                # Check for empty classes
                for cls, task_list in class_structure.items():
                    if len(task_list) == 0:
                        logger.error(f"❌ {filename}: Class '{cls}' has no tasks assigned!")
                        raise ValueError(f"Class '{cls}' in {filename} has no tasks. Each class must have at least one task.")

        # Generate scaffolding per file
        all_results = []

        for filename, file_data in files_map.items():
            file_tasks = file_data['tasks']
            class_structure = file_data['class_structure'] if file_data['class_structure'] else None
            template_vars = list(file_data['template_variables']) if file_data['template_variables'] else None
            # Convert method signatures from sets to lists per class
            method_sigs_by_class = {cls: list(methods) for cls, methods in file_data['method_signatures_by_class'].items()} if file_data['method_signatures_by_class'] else None

            logger.info("=" * 80)
            logger.info(f"🔧 GENERATING CODE FOR: {filename}")
            logger.info(f"  Total Tasks: {len(file_tasks)}")
            if class_structure:
                logger.info(f"  Classes detected: {', '.join(class_structure.keys())}")
            if template_vars:
                logger.info(f"  Template variables to preserve: {template_vars}")
            if method_sigs_by_class:
                logger.info("  📋 METHOD SIGNATURES TO PRESERVE:")
                for cls, methods in method_sigs_by_class.items():
                    logger.info(f"    {cls}: {methods}")
            else:
                logger.info("  ⚠️  NO METHOD SIGNATURES DETECTED - will generate new methods")
            logger.info("=" * 80)

            # Generate for this file only
            file_results = codegen_agent.generate_file_scaffolding(
                filename=filename,
                tasks=file_tasks,
                class_structure=class_structure,
                template_variables=template_vars,
                method_signatures_by_class=method_sigs_by_class
            )

            all_results.extend(file_results)
            logger.info(f"Successfully generated {len(file_results)} tasks for {filename}")

        elapsed_time = time.time() - start_time
        logger.info(f"Total generation completed in {elapsed_time:.2f} seconds")

        logger.info("=" * 80)
        logger.info("RETURNING TO FRONTEND:")
        for idx, result in enumerate(all_results):
            logger.info(f"Task {idx}: {len(result.todos)} todos, file: {result.filename}")
        logger.info("=" * 80)

        return BatchStarterCodeResponse(
            tasks=all_results,
            total_tasks=len(all_results),
            generation_time=f"{elapsed_time:.2f}s"
        )

    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"Failed to generate starter code batch: {e}", exc_info=True)

        if "rate limit" in error_str or "overloaded" in error_str or "529" in error_str:
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily overloaded. Please try again in a few moments."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate starter code batch: {str(e)}"
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
    - Optional test case execution
    """
    try:
        logger.info(f"Executing {request.language} code ({len(request.code)} characters)")

        code_runner = get_code_runner()

        # If test cases are provided, run them
        if request.test_cases and len(request.test_cases) > 0:
            logger.info(f"Running with {len(request.test_cases)} test cases")
            # Convert TestCase objects to dicts
            test_cases_dicts = []
            for tc in request.test_cases:
                if hasattr(tc, 'model_dump'):  # Pydantic v2
                    test_cases_dicts.append(tc.model_dump())
                elif hasattr(tc, 'dict'):  # Pydantic v1
                    test_cases_dicts.append(tc.dict())
                else:
                    test_cases_dicts.append(tc)

            result = code_runner.run_with_tests(request.code, request.language, test_cases_dicts)
        else:
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
# GENERATE TESTS FROM USER CODE
# ============================================

@app.post("/generate-tests", response_model=GenerateTestsResponse)
async def generate_tests(request: GenerateTestsRequest):
    """
    Generate test cases from user's completed code

    Takes the user's code and generates appropriate test cases
    using the same AI model as the initial test generation
    """
    try:
        logger.info(f"Received test generation request for {request.filename}")
        logger.info(f"Language: {request.language}, Code length: {len(request.code)} chars")

        # Generate tests using parser agent
        test_cases = parser_agent.generate_tests_from_code(
            code=request.code,
            language=request.language,
            filename=request.filename,
            assignment_description=request.assignment_description
        )

        if test_cases:
            message = f"Successfully generated {len(test_cases)} test cases"
            logger.info(message)
        else:
            message = "No test cases were generated. Please check your code and try again."
            logger.warning(message)

        return GenerateTestsResponse(
            tests=test_cases,
            message=message
        )

    except Exception as e:
        logger.error(f"Test generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate tests: {str(e)}"
        )


# ============================================
# FEEDBACK
# ============================================

@app.post("/send-feedback", response_model=FeedbackResponse)
async def send_feedback(request: FeedbackRequest):
    """
    Send user feedback via email using Resend API
    """
    try:
        logger.info(f"Received feedback from {request.name} ({request.email})")
        
        resend_service = get_resend_email_service()
        success = resend_service.send_feedback(
            name=request.name,
            email=request.email,
            feedback=request.feedback
        )
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Thank you for your feedback! We'll review it soon."
            )
        else:
            return FeedbackResponse(
                success=False,
                message="Failed to send feedback. Please try again later."
            )
    
    except Exception as e:
        logger.error(f"Error processing feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send feedback: {str(e)}"
        )


# ============================================
# RUN THE APP
# ============================================

if __name__ == "__main__":
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )
