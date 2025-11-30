from pydantic import BaseModel
from typing import List, Optional, Dict


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
    template_variables: Optional[List[str]] = None  # NEW: for template preservation

# NEW: Class Schema for multi-class file support
class ClassSchema(BaseModel):
    class_name: str
    purpose: str
    tasks: List[TaskSchema]
    method_signatures: Optional[List[str]] = []  # Method names/signatures to preserve from template

# NEW: Template Structure Schema
class TemplateStructure(BaseModel):
    has_template: bool = False
    variable_names: List[str] = []
    class_names: List[str] = []
    method_signatures: Optional[List[str]] = []

# NEW: File Schema for multi-file support (updated for classes)
class FileSchema(BaseModel):
    filename: str
    purpose: str
    tasks: Optional[List[TaskSchema]] = None  # For simple files
    classes: Optional[List[ClassSchema]] = None  # For multi-class files
    tests: Optional[List['TestCase']] = None  # Per-file test cases

#Test Case Schema
class TestCase(BaseModel):
    test_name: str  # e.g., "test_empty_input"
    function_name: str  # The function being tested
    input_data: str  # Input as string (could be JSON for complex inputs)
    expected_output: str  # Expected output as string
    description: str  # Human-readable description
    test_type: str  # "normal", "edge", or "error"

#Output
class TaskBreakdownSchema(BaseModel):
    overview: str
    total_estimated_time: str
    template_structure: Optional[TemplateStructure] = None  # NEW: template info
    files: List[FileSchema]  # Changed from: tasks: List[TaskSchema]



#--------Schema for Agent 2: BoilerPlate Code Generator--------#

#Input
class BoilerPlateCodeSchema(BaseModel):
    task_description: str
    programming_language: str
    concepts: List[str]
    known_language: Optional[str] = None
    experience_level: Optional[str] = None
    filename: str  # NEW: which file this task belongs to

    # NEW FIELDS for class and template support
    class_name: Optional[str] = None
    template_variables: Optional[List[str]] = None
    method_signatures: Optional[List[str]] = None  # Method names to preserve from template

#Output
class StarterCode(BaseModel):
    code_snippet: str
    instructions: str
    todos: List[str]
    concept_examples: Optional[Dict[str, str]] = None
    filename: str  # NEW: which file this task belongs to

# Input - batch of code generation requests
class BatchBoilerPlateCodeSchema(BaseModel):
    tasks: List[BoilerPlateCodeSchema]

# Output - batch of starter codes
class BatchStarterCodeResponse(BaseModel):
    tasks: List[StarterCode]
    total_tasks: int
    generation_time: Optional[str] = None

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
   experience_level: Optional[str] = None
   test_results: Optional[List[Dict]] = None  # NEW: Test results to help debug test failures

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
    stdin: Optional[str] = None  # Optional stdin input for input() calls
    test_cases: Optional[List[TestCase]] = None  # Optional test cases to run

# Individual Test Result
class TestResult(BaseModel):
    test_name: str
    function_name: Optional[str] = None  # Function being tested
    passed: bool
    input_data: str
    expected_output: str
    actual_output: str
    error: Optional[str] = None

#Output
class CodeExecutionResult(BaseModel):
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: str
    test_results: Optional[List[TestResult]] = None
    tests_passed: Optional[int] = None
    tests_failed: Optional[int] = None


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


#--------Schema for Test Generation from User Code--------#

#Input
class GenerateTestsRequest(BaseModel):
    code: str  # User's completed code
    language: str  # Programming language
    filename: str  # Filename for context
    assignment_description: Optional[str] = None  # Optional: original assignment for context

#Output
class GenerateTestsResponse(BaseModel):
    tests: List[TestCase]
    message: str


