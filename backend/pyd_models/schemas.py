from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


#--------Schema for Agent 1: Parser--------#

#Input
class AssignmentSchema(BaseModel):
    assignment_text: str
    target_language: str
    known_language: Optional[str] = None
    experience_level: str


class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    dependencies: List[int]
    estimated_time: str
    concepts: List[str]

#Output
class TaskBreakdownSchema(BaseModel):
    tasks: List[TaskSchema]
    overview: str
    total_estimated_time: str



#--------Schema for Agent 2: BoilerPlate Code Generator--------#

#Input
class BoilerPlateCodeSchema(BaseModel):
    task_description: str
    programming_language: str
    concepts: List[str]
    known_language: Optional[str] = None

#Output
class StarterCode(BaseModel):
    code_snippet: str
    instructions: str
    todos: List[str]
    concept_examples: Optional[Dict[str, str]] = None

#--------Schema for Agent 3: Live Helper--------#

#Input
class HintResponseSchema(BaseModel):
   task_description: str
   concepts: List[str]
   student_code: str
   question: str
   previous_hints: List[str]
   help_count: int
   known_language: Optional[str] = None
   target_language: Optional[str] = None

#Output
class HintSchema(BaseModel):
    hint: str
    hint_type: str
    example_code: Optional[str] = None


#--------Schema for Code Execution--------#

#Input
class CodeExecutionRequest(BaseModel):
    code: str
    language: str

#Output
class CodeExecutionResult(BaseModel):
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: str


#--------Schema for PDF Text Extraction--------#

#Output
class PDFExtractionResult(BaseModel):
    success: bool
    extracted_text: str
    page_count: int
    error: Optional[str] = None


#--------Schema for Concept Example (On-Demand)--------#

#Input
class ConceptExampleRequest(BaseModel):
    concept: str
    programming_language: str
    known_language: Optional[str] = None
    context: Optional[str] = None  # Optional: what they're trying to do

#Output
class ConceptExampleResponse(BaseModel):
    concept: str
    example_type: str  # "basic_syntax", "intermediate_pattern", "advanced_pattern"
    code_example: str
    explanation: str
    comparison_to_known: Optional[str] = None  # If known_language provided


# #--------Schema for Agent 4: Code Reviewer/Guidance--------#


