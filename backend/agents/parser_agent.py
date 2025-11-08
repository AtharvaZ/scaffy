""" Agent 1 for parsing tasks. 
Parse Assignments and break tem down into smaller task with dependencies.
"""

from pyd_models.schemas import AssignmentSchema, TaskBreakdownSchema
from services import get_anthropic_client
from utils.agent_prompts import get_parser_prompt
from utils.json_parser import extract_json_from_response, validate_task_breakdown

#Agent responsible for parsing assignments and creating task breakdowns
class ParserAgent:

    def __init__(self):
        self.client = get_anthropic_client()

    def parse_assignment(self, inputData: AssignmentSchema) -> TaskBreakdownSchema:
        prompt = get_parser_prompt(
            assignment_text=inputData.assignment_text,
            target_language=inputData.target_language,
            known_language=inputData.known_language,
            experience_level=inputData.experirence_level
        )

        response_text = self.client.generate_response(prompt, max_tokens=4000)

        data = extract_json_from_response(response_text)
        validate_task_breakdown(data)

        return TaskBreakdownSchema(**data)

parser_agent = None

def get_parser_agent() -> ParserAgent:
    global parser_agent
    if parser_agent is None:
        parser_agent = ParserAgent()
    return parser_agent
