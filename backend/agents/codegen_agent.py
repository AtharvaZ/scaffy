""" Agent 2 for boiler plate code generation tasks.
Generates starter code templates with TODO comments for specific tasks
"""

import logging
from typing import List
from pyd_models.schemas import BoilerPlateCodeSchema, StarterCode
from services import get_anthropic_client
from utils.agent_prompts import get_batch_codegen_prompt
from utils.json_parser import extract_json_from_response

logger = logging.getLogger(__name__)

# Agent responsible for generating boilerplate code templates
class CodegenAgent:

    def __init__(self):
        self.client = get_anthropic_client()
        self.max_retries = 3

    def generate_all_boilerplate_batch(self, tasks_data: List[BoilerPlateCodeSchema]) -> List[StarterCode]:
   
        if not tasks_data:
            raise ValueError("No tasks provided for batch generation")
        
        # Convert BoilerPlateCodeSchema objects to dicts for the prompt function
        tasks_dict_list = []
        for task in tasks_data:
            tasks_dict_list.append({
                'task_description': task.task_description,
                'programming_language': task.programming_language,
                'concepts': task.concepts,
                'known_language': task.known_language
            })
        
        # Get the batch prompt from agent_prompts
        prompt = get_batch_codegen_prompt(tasks_dict_list)
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Batch Codegen for {len(tasks_data)} tasks, attempt {attempt + 1}/{self.max_retries}")
                
                # Use higher max_tokens for batch (but still reasonable)
                # Roughly 300-500 tokens per task
                estimated_tokens = len(tasks_data) * 400
                max_tokens = min(estimated_tokens + 500, 8000)
                
                response_text = self.client.generate_response(prompt, max_tokens=max_tokens)
                
                data = extract_json_from_response(response_text)
                
                # Validate response structure
                if "tasks" not in data:
                    raise ValueError("Response missing 'tasks' field")
                
                if not isinstance(data["tasks"], list):
                    raise ValueError("'tasks' must be a list")
                
                if len(data["tasks"]) != len(tasks_data):
                    raise ValueError(f"Expected {len(tasks_data)} tasks, got {len(data['tasks'])}")
                
                # Convert to StarterCode objects
                results = []
                for i, task_data in enumerate(data["tasks"], 1):
                    # Validate required fields for this task
                    if "code_snippet" not in task_data and "code" not in task_data:
                        raise ValueError(f"Task {i} missing 'code_snippet' or 'code' field")
                    if "instructions" not in task_data:
                        raise ValueError(f"Task {i} missing 'instructions' field")
                    if "todos" not in task_data:
                        raise ValueError(f"Task {i} missing 'todos' field")

                    # Map "code" to "code_snippet" if needed
                    if "code" in task_data and "code_snippet" not in task_data:
                        task_data["code_snippet"] = task_data["code"]

                    # Log the todos for debugging
                    logger.info(f"Task {i} todos: {task_data['todos']}")

                    # Create StarterCode object
                    results.append(StarterCode(
                        code_snippet=task_data["code_snippet"],
                        instructions=task_data["instructions"],
                        todos=task_data["todos"],
                        concept_examples=None  # Always null - generated on-demand
                    ))

                logger.info(f"Successfully generated {len(results)} starter codes in batch on attempt {attempt + 1}")
                logger.info("=" * 80)
                logger.info("BATCH GENERATION SUMMARY:")
                for idx, result in enumerate(results):
                    logger.info(f"Task {idx}: {len(result.todos)} todos")
                logger.info("=" * 80)
                return results
                
            except Exception as e:
                # Check if it's an API error
                error_str = str(e).lower()
                if "rate limit" in error_str or "overloaded" in error_str or "529" in error_str:
                    logger.error(f"API error during batch generation: {str(e)}")
                    raise Exception(f"API service is temporarily unavailable. Please try again in a few moments. Error: {str(e)}")
                
                # For JSON parsing errors, retry
                if isinstance(e, (ValueError, KeyError)):
                    last_error = e
                    logger.warning(f"Batch attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < self.max_retries - 1:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed. Ensure response is ONLY valid JSON with all {len(tasks_data)} tasks."
                    continue
                else:
                    # For other errors, don't retry
                    logger.error(f"Unexpected error during batch generation: {str(e)}")
                    raise
        
        # If all retries failed
        logger.error(f"All {self.max_retries} batch attempts failed")
        raise ValueError(f"Failed to generate batch code after {self.max_retries} attempts: {str(last_error)}")

codegen_agent = None
def get_batch_codegen_agent() -> CodegenAgent:
    global codegen_agent
    if codegen_agent is None:
        codegen_agent = CodegenAgent()
    return codegen_agent