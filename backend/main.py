from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from dotenv import load_dotenv

from pyd_models.schemas import (
    AssignmentSchema,
    TaskBreakdownSchema,
    BoilerPlateCodeSchema,
    StarterCode,
    HintResponseSchema,
    HintSchema
)

# Import agents
from agents.parser_agent import ParserAgent
from agents.codegen_agent import CodegenAgent
from agents.live_helper import LiveHelperAgent

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
        result = codegen_agent.generate_starter_code(request)
        return result
    
    except Exception as e:
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
        result = helper_agent.get_hint(request)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate hint: {str(e)}"
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