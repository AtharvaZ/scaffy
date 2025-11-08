from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


#--------Schema for Agent 1: Parser--------#

class AssignmentSchema(BaseModel):
    assignment_text: str
    target_language: str
    known_language: Optional[str] = None
    experirence_level: str


class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    dependencies: List[int]
    estimaeted_time: str
    concepts: List[str]

class TaskBreakdownSchema(BaseModel):
    task: List[TaskSchema]
    overview: str
    total_estimated_time: str



#--------Schema for Agent 2: BoilerPlate Code Generator--------#

class BoilerPlateCodeSchema(BaseModel):
    task_description: str
    programming_language: str
    concepts: List[str]
    known_language: Optional[str] = None

class StarterCodeSchema(BaseModel):
    code_snippet: str
    instructions: str
    todos: List[str]
    concept_examples: Optional[Dict[str, str]] = None

#--------Schema for Agent 3: Live Helper--------#

class HintResponseSchema(BaseModel):
   task_description: str
   concepts: List[str]
   student_code: str
   question: str
   previous_hints: List[str]
   help_count: int
   known_language: Optional[str] = None
   target_language: Optional[str] = None

class HintSchema(BaseModel):
    hint: str
    hint_type: str
    example_code: Optional[str] = None


#--------Schema for Agent 4: Code Reviewer/Guidance--------#

class SyntaxRequest(BaseModel):
    concept: str
    target_language: str
    known_language: Optional[str] = None

class SyntaxGuidance(BaseModel):
    concept: str
    target_syntax: str
    explanation: str
    known_syntax: Optional[str] = None
    comparison: Optional[str] = None
    examples: List[str]