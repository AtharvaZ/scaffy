""" Agent 1 for parsing tasks.
Parse Assignments and break them down into smaller tasks with dependencies.
"""

import logging
import json
from typing import List
from pyd_models.schemas import AssignmentSchema, TaskBreakdownSchema, TestCase
from services import get_anthropic_client
from utils.agent_prompts import get_parser_prompt, get_test_generation_prompt
from utils.json_parser import extract_json_from_response, validate_task_breakdown

logger = logging.getLogger(__name__)

#Agent responsible for parsing assignments and creating task breakdowns
class ParserAgent:

    def __init__(self):
        self.client = get_anthropic_client()
        self.max_retries = 3

    def generate_test_cases(self, assignment_text: str, files: list, target_language: str) -> List[TestCase]:
        """
        Generate test cases based on assignment requirements (UPDATED FOR MULTI-FILE)

        Args:
            assignment_text: Full assignment description
            files: List of file structures from task breakdown
            target_language: Programming language (Python, Java, C++, etc.)

        Returns:
            List of TestCase objects, or empty list if generation fails
        """
        try:
            logger.info("Generating test cases...")

            # Convert files to dict if they're FileSchema objects
            files_list = []
            for file_obj in files:
                if hasattr(file_obj, 'model_dump'):  # Pydantic v2
                    files_list.append(file_obj.model_dump())
                elif hasattr(file_obj, 'dict'):  # Pydantic v1
                    files_list.append(file_obj.dict())
                else:
                    files_list.append(file_obj)

            prompt = get_test_generation_prompt(assignment_text, files_list, target_language)

            # Try to generate test cases with retries
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Test generation attempt {attempt + 1}/{self.max_retries}")
                    response_text = self.client.generate_response(prompt, max_tokens=2500)

                    # Extract JSON array from response
                    test_data = extract_json_from_response(response_text)

                    # If response is a dict with 'tests' key, extract it
                    if isinstance(test_data, dict) and 'tests' in test_data:
                        test_data = test_data['tests']

                    # Ensure it's a list
                    if not isinstance(test_data, list):
                        raise ValueError("Test data must be a list")

                    # Validate and create TestCase objects
                    test_cases = []
                    for test in test_data:
                        try:
                            test_case = TestCase(**test)
                            test_cases.append(test_case)
                        except Exception as e:
                            logger.warning(f"Skipping invalid test case: {e}")
                            continue

                    logger.info(f"Successfully generated {len(test_cases)} test cases")
                    return test_cases

                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    logger.warning(f"Test generation attempt {attempt + 1} failed: {str(e)}")

                    if attempt < self.max_retries - 1:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed. Ensure your response is ONLY a valid JSON array starting with [ and ending with ]."
                    continue

            logger.warning("Failed to generate test cases after all retries, returning empty list")
            return []

        except Exception as e:
            logger.error(f"Unexpected error generating test cases: {str(e)}")
            return []  # Return empty list instead of crashing


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
        task_breakdown_result = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Parser Agent attempt {attempt + 1}/{self.max_retries}")
                response_text = self.client.generate_response(prompt, max_tokens=2000)

                data = extract_json_from_response(response_text)
                validate_task_breakdown(data)

                logger.info(f"Successfully parsed assignment on attempt {attempt + 1}")
                task_breakdown_result = data
                break

            except (ValueError, KeyError) as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                # If not the last attempt, add a note to the prompt to be more strict
                if attempt < self.max_retries - 1:
                    prompt += f"\n\nIMPORTANT: Previous attempt failed due to invalid JSON format. Ensure your response is ONLY valid JSON with no additional text."
                continue

        # If all retries failed, raise the last error
        if task_breakdown_result is None:
            logger.error(f"All {self.max_retries} attempts failed")
            raise ValueError(f"Failed to parse assignment after {self.max_retries} attempts: {str(last_error)}")

        # Generate test cases
        test_cases = self.generate_test_cases(
            assignment_text=inputData.assignment_text,
            files=task_breakdown_result['files'],
            target_language=inputData.target_language
        )

        # Add tests to the result
        task_breakdown_result['tests'] = test_cases

        return TaskBreakdownSchema(**task_breakdown_result)

parser_agent = None

def get_parser_agent() -> ParserAgent:
    global parser_agent
    if parser_agent is None:
        parser_agent = ParserAgent()
    return parser_agent
