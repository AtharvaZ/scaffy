""" Agent 2 for boiler plate code generation tasks.
Generates starter code templates with TODO comments for specific tasks
"""

import logging
from typing import List
from pyd_models.schemas import BoilerPlateCodeSchema, StarterCode
from services import get_anthropic_client
from utils.json_parser import extract_json_from_response

logger = logging.getLogger(__name__)

# Agent responsible for generating boilerplate code templates
class CodegenAgent:

    def __init__(self):
        # Use Sonnet 4 for codegen - best quality for complex code generation
        self.client = get_anthropic_client(model="claude-sonnet-4-20250514")
        self.max_retries = 3

    def generate_file_scaffolding(self, filename: str,
                                   tasks: List[BoilerPlateCodeSchema],
                                   class_structure: dict = None,
                                   template_variables: list = None,
                                   method_signatures_by_class: dict = None) -> List[StarterCode]:
        """
        Generate scaffolding for ONE complete file.

        Args:
            filename: Name of file to generate
            tasks: List of tasks for this file
            class_structure: Dict of {class_name: [tasks]} or None for single-class
            template_variables: List of variable names from template to preserve, or None
            method_signatures_by_class: Dict of {class_name: [method_names]} for template methods

        Returns:
            List of StarterCode objects for this file's tasks
        """

        if not tasks:
            raise ValueError(f"No tasks provided for {filename}")

        # Convert tasks to dict format for prompt
        tasks_dict_list = []
        for task in tasks:
            task_dict = {
                'task_description': task.task_description,
                'programming_language': task.programming_language,
                'concepts': task.concepts,
                'known_language': task.known_language,
                'filename': task.filename,
                'experience_level': getattr(task, 'experience_level', 'intermediate'),
                'class_name': getattr(task, 'class_name', None),
                'template_variables': getattr(task, 'template_variables', None)
            }
            tasks_dict_list.append(task_dict)

        # Get focused prompt for THIS file
        from utils.agent_prompts import get_file_codegen_prompt

        prompt = get_file_codegen_prompt(
            tasks_dict_list,
            filename,
            class_structure=class_structure,
            template_variables=template_variables,
            method_signatures_by_class=method_signatures_by_class
        )

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"File codegen for {filename}, attempt {attempt + 1}/{self.max_retries}")

                # Smart token allocation (like the working version)
                # Estimate based on task count - keep it reasonable
                estimated_tokens = len(tasks) * 300  # ~300 tokens per task
                max_tokens = min(estimated_tokens + 1000, 4000)  # Cap at 4000 like before

                logger.info(f"Using {max_tokens} max tokens for {len(tasks)} tasks in {filename}")

                response_text = self.client.generate_response(prompt, max_tokens=max_tokens)

                # Log the response for debugging
                logger.info(f"AI response preview (first 500 chars): {response_text[:500]}")
                logger.info(f"Response length: {len(response_text)} chars")
                logger.info(f"Last 200 chars: {response_text[-200:]}")

                # Save full response to temp file for debugging on first attempt
                if attempt == 0:
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        f.write(response_text)
                        logger.info(f"Full response saved to: {f.name}")

                data = extract_json_from_response(response_text)

                # Log what keys we got
                logger.info(f"Parsed JSON keys: {list(data.keys())}")
                logger.info(f"Data type: {type(data)}")

                # Check if response was truncated by looking at the end
                if not response_text.strip().endswith('}'):
                    logger.warning(f"Response appears truncated (doesn't end with }}). Length: {len(response_text)}")
                    logger.warning(f"Last 100 chars: {response_text[-100:]}")
                    raise ValueError(f"Response truncated at {len(response_text)} chars. Need more tokens.")

                # Validate response - handle both correct format and single task fallback
                if "tasks" not in data:
                    # Check if we got a single task object instead of wrapper
                    if "task_number" in data and "code_snippet" in data:
                        logger.warning(f"Got single task object instead of wrapper")
                        logger.warning(f"Response likely truncated - outermost }} missing")
                        raise ValueError(f"Response incomplete: got single task object, expected {{\"tasks\": [...]}} wrapper with {len(tasks)} tasks")
                    else:
                        logger.error(f"Response missing 'tasks' field. Got keys: {list(data.keys())}")
                        logger.error(f"Full parsed data: {data}")
                        raise ValueError(f"Response missing 'tasks' field. Got: {list(data.keys())}")

                if not isinstance(data["tasks"], list):
                    raise ValueError("'tasks' must be a list")

                if len(data["tasks"]) != len(tasks):
                    raise ValueError(f"Expected {len(tasks)} tasks, got {len(data['tasks'])}")

                # Convert to StarterCode objects
                results = []
                for i, task_data in enumerate(data["tasks"], 1):
                    if "code_snippet" not in task_data and "code" not in task_data:
                        raise ValueError(f"Task {i} missing 'code_snippet' or 'code' field")
                    if "instructions" not in task_data:
                        raise ValueError(f"Task {i} missing 'instructions' field")
                    if "todos" not in task_data:
                        raise ValueError(f"Task {i} missing 'todos' field")
                    if "filename" not in task_data:
                        task_data["filename"] = filename

                    if "code" in task_data and "code_snippet" not in task_data:
                        task_data["code_snippet"] = task_data["code"]

                    results.append(StarterCode(
                        code_snippet=task_data["code_snippet"],
                        instructions=task_data["instructions"],
                        todos=task_data["todos"],
                        concept_examples=None,
                        filename=task_data["filename"]
                    ))

                logger.info(f"Successfully generated {len(results)} tasks for {filename}")
                return results

            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"File codegen attempt {attempt + 1} failed: {error_msg}")

                if attempt < self.max_retries - 1:
                    # Provide specific guidance based on error type
                    if "missing 'tasks' field" in error_msg.lower():
                        prompt += f"\n\nCRITICAL ERROR: Your response MUST have a 'tasks' array at the top level. Structure: {{\"tasks\": [{{task1}}, {{task2}}, ...]}}. Generate ALL {len(tasks)} tasks inside the array."
                    else:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed: {error_msg}. Ensure response is ONLY valid JSON with all {len(tasks)} tasks in a 'tasks' array."
                continue

        logger.error(f"All {self.max_retries} attempts failed for {filename}")
        raise ValueError(f"Failed to generate scaffolding for {filename} after {self.max_retries} attempts: {str(last_error)}")

codegen_agent = None
def get_batch_codegen_agent() -> CodegenAgent:
    global codegen_agent
    if codegen_agent is None:
        codegen_agent = CodegenAgent()
    return codegen_agent