""" Agent 2 for boiler plate code generation tasks.
Generates starter code templates with TODO comments for specific tasks
"""

import logging
from pyd_models.schemas import BoilerPlateCodeSchema, StarterCode
from services import get_anthropic_client
from utils.agent_prompts import get_codegen_prompt
from utils.json_parser import extract_json_from_response

logger = logging.getLogger(__name__)

# Agent responsible for generating boilerplate code templates
class CodegenAgent:

    def __init__(self):
        self.client = get_anthropic_client()
        self.max_retries = 3

    def generate_boilerplate_code(self, inputData: BoilerPlateCodeSchema) -> StarterCode:
        """
        Generate boilerplate code with retry logic for robust JSON extraction.
        Retries up to max_retries times if JSON parsing fails.
        """
        prompt = get_codegen_prompt(
            task_description=inputData.task_description,
            language=inputData.programming_language,
            concepts=inputData.concepts,
            known_language=inputData.known_language
        )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Codegen Agent attempt {attempt + 1}/{self.max_retries}")
                response_text = self.client.generate_response(prompt, max_tokens=2500)
                
                data = extract_json_from_response(response_text)

                # Validate required fields - check both "code" and "code_snippet"
                requirements = ["instructions", "todos"]
                for req in requirements:
                    if req not in data:
                        raise ValueError(f"Missing required field '{req}' in the response data.")
                
                # Check for code field (accept either "code" or "code_snippet")
                if "code_snippet" not in data and "code" not in data:
                    raise ValueError("Missing required field 'code_snippet' or 'code' in the response data.")
                
                # Map "code" to "code_snippet" to match StarterCode schema
                if "code" in data and "code_snippet" not in data:
                    data["code_snippet"] = data["code"]
                    del data["code"]
                    
                # Always set concept_examples to null - examples are generated on-demand
                data["concept_examples"] = None

                logger.info(f"Successfully generated code on attempt {attempt + 1}")
                return StarterCode(**data)
                
            except Exception as e:
                # Check if it's an API error (rate limit, overloaded, etc.)
                error_str = str(e).lower()
                if "rate limit" in error_str or "overloaded" in error_str or "529" in error_str:
                    # API errors are already handled by the client with retries
                    # Just re-raise them with a user-friendly message
                    logger.error(f"API error during code generation: {str(e)}")
                    raise Exception(f"API service is temporarily unavailable. Please try again in a few moments. Error: {str(e)}")
                
                # For JSON parsing errors, retry with updated prompt
                if isinstance(e, (ValueError, KeyError)):
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    # If not the last attempt, add a note to the prompt to be more strict
                    if attempt < self.max_retries - 1:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed due to invalid JSON format. Ensure your response is ONLY valid JSON with no additional text."
                    continue
                else:
                    # For other errors, don't retry
                    logger.error(f"Unexpected error during code generation: {str(e)}")
                    raise
        
        # If all retries failed, raise the last error
        logger.error(f"All {self.max_retries} attempts failed")
        raise ValueError(f"Failed to generate code after {self.max_retries} attempts: {str(last_error)}")

codegen_agent = None
def get_codegen_agent() -> CodegenAgent:
    global codegen_agent
    if codegen_agent is None:
        codegen_agent = CodegenAgent()
    return codegen_agent