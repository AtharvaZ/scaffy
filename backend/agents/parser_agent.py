""" Agent 1 for parsing tasks. 
Parse Assignments and break them down into smaller tasks with dependencies.
"""

import logging
from pyd_models.schemas import AssignmentSchema, TaskBreakdownSchema
from services import get_anthropic_client
from utils.agent_prompts import get_parser_prompt
from utils.json_parser import extract_json_from_response, validate_task_breakdown

logger = logging.getLogger(__name__)

#Agent responsible for parsing assignments and creating task breakdowns
class ParserAgent:

    def __init__(self):
        self.client = get_anthropic_client()
        self.max_retries = 3

    def parse_assignment(self, inputData: AssignmentSchema) -> TaskBreakdownSchema:
        """
        Parse assignment with retry logic for robust JSON extraction.
        Retries up to max_retries times if JSON parsing fails.
        """
        prompt = get_parser_prompt(
            assignment_text=inputData.assignment_text,
            target_language=inputData.target_language,
            known_language=inputData.known_language,
            experience_level=inputData.experience_level
        )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Parser Agent attempt {attempt + 1}/{self.max_retries}")
                response_text = self.client.generate_response(prompt, max_tokens=4000)
                
                data = extract_json_from_response(response_text)
                validate_task_breakdown(data)
                
                logger.info(f"Successfully parsed assignment on attempt {attempt + 1}")
                return TaskBreakdownSchema(**data)
                
            except (ValueError, KeyError) as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # If not the last attempt, add a note to the prompt to be more strict
                if attempt < self.max_retries - 1:
                    prompt += f"\n\nIMPORTANT: Previous attempt failed due to invalid JSON format. Ensure your response is ONLY valid JSON with no additional text."
                continue
        
        # If all retries failed, raise the last error
        logger.error(f"All {self.max_retries} attempts failed")
        raise ValueError(f"Failed to parse assignment after {self.max_retries} attempts: {str(last_error)}")

parser_agent = None

def get_parser_agent() -> ParserAgent:
    global parser_agent
    if parser_agent is None:
        parser_agent = ParserAgent()
    return parser_agent
