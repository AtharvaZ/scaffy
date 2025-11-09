"""Agent 3 for live helper tasks.
Provides contextual hints to students while they code
"""

import logging
from pyd_models.schemas import HintResponseSchema, HintSchema
from services import get_anthropic_client
from utils.agent_prompts import get_helper_prompt
from utils.json_parser import extract_json_from_response

logger = logging.getLogger(__name__)

# Agent responsible for providing live coding hints
class LiveHelperAgent:
    
    def __init__(self):
        self.client = get_anthropic_client()
        self.max_retries = 3

    def provide_hint(self, inputData: HintResponseSchema) -> HintSchema:
        """
        Provide hint with retry logic for robust JSON extraction.
        Retries up to max_retries times if JSON parsing fails.
        """
        prompt = get_helper_prompt(
            task_description=inputData.task_description,
            concepts=inputData.concepts,
            student_code=inputData.student_code,
            question=inputData.question,
            previous_hints=inputData.previous_hints,
            help_count=inputData.help_count,
            known_language=inputData.known_language,
            target_language=inputData.target_language
        )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Live Helper Agent attempt {attempt + 1}/{self.max_retries}")
                response_text = self.client.generate_response(prompt, max_tokens=1000)
                
                data = extract_json_from_response(response_text)

                requirements = ["hint", "hint_type"]
                for req in requirements:
                    if req not in data:
                        raise ValueError(f"Missing required field '{req}' in the response data.")
                    
                if "example_code" not in data:
                    data["example_code"] = None

                logger.info(f"Successfully generated hint on attempt {attempt + 1}")
                return HintSchema(**data)
                
            except (ValueError, KeyError) as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # If not the last attempt, add a note to the prompt to be more strict
                if attempt < self.max_retries - 1:
                    prompt += f"\n\nIMPORTANT: Previous attempt failed due to invalid JSON format. Ensure your response is ONLY valid JSON with no additional text."
                continue
        
        # If all retries failed, raise the last error
        logger.error(f"All {self.max_retries} attempts failed")
        raise ValueError(f"Failed to generate hint after {self.max_retries} attempts: {str(last_error)}")
    
live_helper_agent = None
def get_live_helper_agent() -> LiveHelperAgent:
    global live_helper_agent
    if live_helper_agent is None:
        live_helper_agent = LiveHelperAgent()
    return live_helper_agent