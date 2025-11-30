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
        # Use Haiku for parser - fast and cost-effective for structured output
        self.client = get_anthropic_client(model="claude-3-5-haiku-20241022")
        self.max_retries = 3

    def generate_test_cases_for_file(self, assignment_text: str, file_data: dict, target_language: str) -> List[TestCase]:
        """
        Generate test cases for a SINGLE file (PER-FILE GENERATION)

        Args:
            assignment_text: Full assignment description for context
            file_data: Single file structure (dict with filename, purpose, tasks/classes)
            target_language: Programming language (Python, Java, C++, etc.)

        Returns:
            List of TestCase objects for this file, or empty list if generation fails
        """
        try:
            filename = file_data.get('filename', 'unknown')
            logger.info("=" * 80)
            logger.info(f"STARTING TEST GENERATION FOR FILE: {filename}")
            logger.info(f"Target Language: {target_language}")
            logger.info("=" * 80)

            # Convert file_data to dict if it's a FileSchema object
            if hasattr(file_data, 'model_dump'):  # Pydantic v2
                file_dict = file_data.model_dump()
            elif hasattr(file_data, 'dict'):  # Pydantic v1
                file_dict = file_data.dict()
            else:
                file_dict = file_data

            prompt = get_test_generation_prompt(assignment_text, [file_dict], target_language)

            # Try to generate test cases with retries
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Test generation for {filename}: attempt {attempt + 1}/{self.max_retries}")
                    response_text = self.client.generate_response(prompt, max_tokens=2500)

                    logger.info(f"Received response from AI for {filename} (length: {len(response_text)} chars)")
                    logger.debug(f"Response preview: {response_text[:500]}")

                    # Extract JSON array from response
                    test_data = extract_json_from_response(response_text)

                    # If response is a dict with 'tests' key, extract it
                    if isinstance(test_data, dict) and 'tests' in test_data:
                        test_data = test_data['tests']

                    # Ensure it's a list
                    if not isinstance(test_data, list):
                        raise ValueError(f"Test data must be a list, got {type(test_data)}")

                    # Validate and create TestCase objects
                    test_cases = []
                    for idx, test in enumerate(test_data):
                        try:
                            test_case = TestCase(**test)
                            test_cases.append(test_case)
                        except Exception as e:
                            logger.warning(f"Skipping invalid test case {idx}: {e} - Data: {test}")
                            continue

                    logger.info("=" * 80)
                    logger.info(f"✓ Successfully generated {len(test_cases)} test cases for {filename}")
                    logger.info("=" * 80)
                    return test_cases

                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    logger.warning(f"Test generation for {filename} attempt {attempt + 1} failed: {str(e)}")

                    if attempt < self.max_retries - 1:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed. Ensure your response is ONLY a valid JSON array starting with [ and ending with ]."
                    continue

            logger.error("=" * 80)
            logger.error(f"✗ FAILED to generate test cases for {filename} after all retries")
            logger.error("Returning empty list")
            logger.error("=" * 80)
            return []

        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"✗ UNEXPECTED ERROR generating test cases for {filename}: {str(e)}")
            logger.error("Returning empty list")
            logger.error("=" * 80)
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
                response_text = self.client.generate_response(prompt, max_tokens=3000)

                # Log response for debugging
                logger.info(f"AI response preview (first 500 chars): {response_text[:500]}")

                data = extract_json_from_response(response_text)

                # Log parsed data keys
                logger.info(f"Parsed JSON keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")

                # Log template structure detection
                template_structure = data.get('template_structure', {})
                if template_structure and template_structure.get('has_template'):
                    logger.info("=" * 80)
                    logger.info("📋 TEMPLATE STRUCTURE DETECTED:")
                    logger.info(f"  Has Template: {template_structure.get('has_template')}")
                    logger.info(f"  Class Names: {template_structure.get('class_names', [])}")
                    logger.info(f"  Variable Names: {template_structure.get('variable_names', [])}")
                    logger.info(f"  Global Method Signatures: {template_structure.get('method_signatures', [])}")
                    logger.info("=" * 80)

                # Log detected files and classes with methods
                files_list = data.get('files', [])
                logger.info("=" * 80)
                logger.info(f"📁 DETECTED {len(files_list)} FILE(S):")
                for file_idx, file_data in enumerate(files_list, 1):
                    filename = file_data.get('filename', 'unknown')
                    logger.info(f"\n  FILE {file_idx}: {filename}")
                    logger.info(f"    Purpose: {file_data.get('purpose', 'N/A')}")

                    # Check if file has classes
                    classes = file_data.get('classes', [])
                    if classes:
                        logger.info(f"    Classes: {len(classes)} detected")
                        for class_idx, cls in enumerate(classes, 1):
                            class_name = cls.get('class_name', 'Unknown')
                            method_sigs = cls.get('method_signatures', [])
                            logger.info(f"      CLASS {class_idx}: {class_name}")
                            logger.info(f"        Purpose: {cls.get('purpose', 'N/A')}")
                            logger.info(f"        Method Signatures: {method_sigs}")
                            logger.info(f"        Tasks: {len(cls.get('tasks', []))}")
                    else:
                        # Simple file with tasks
                        tasks = file_data.get('tasks', [])
                        logger.info(f"    Simple file with {len(tasks)} tasks (no classes)")
                logger.info("=" * 80)

                validate_task_breakdown(data)

                logger.info(f"Successfully parsed assignment on attempt {attempt + 1}")
                task_breakdown_result = data
                break

            except (ValueError, KeyError) as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")

                # If not the last attempt, add specific guidance based on the error
                if attempt < self.max_retries - 1:
                    if "overview" in error_msg:
                        prompt += f"\n\nCRITICAL: Your response MUST start with the 'overview' field at the top level. Structure: {{\"overview\": \"...\", \"total_estimated_time\": \"...\", \"template_structure\": {{...}}, \"files\": [...]}}"
                    else:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed: {error_msg}. Ensure your response is ONLY valid JSON with ALL required fields."
                continue

        # If all retries failed, raise the last error
        if task_breakdown_result is None:
            logger.error(f"All {self.max_retries} attempts failed")
            raise ValueError(f"Failed to parse assignment after {self.max_retries} attempts: {str(last_error)}")

        # DISABLED: Automatic test generation during parsing
        # Tests are now generated on-demand when user clicks "Generate Tests" button
        # This allows the AI to analyze the user's actual code, not just the boilerplate
        files_list = task_breakdown_result.get('files', [])
        if files_list:
            logger.info(f"Skipping automatic test generation for {len(files_list)} files")
            logger.info("Tests will be generated on-demand from user's code")
            for file_data in files_list:
                # Initialize with empty test array
                file_data['tests'] = []
        else:
            logger.warning("No files found, initializing with empty tests")

        return TaskBreakdownSchema(**task_breakdown_result)

    def generate_tests_from_code(self, code: str, language: str, filename: str, assignment_description: str = None) -> List[TestCase]:
        """
        Generate test cases from user's completed code.

        Args:
            code: User's completed code
            language: Programming language
            filename: Filename for context
            assignment_description: Optional assignment description for context

        Returns:
            List of TestCase objects
        """
        try:
            logger.info("=" * 80)
            logger.info(f"GENERATING TESTS FROM USER CODE: {filename}")
            logger.info(f"Language: {language}")
            logger.info(f"Code length: {len(code)} chars")
            logger.info("=" * 80)

            # Build context from code and assignment
            if assignment_description:
                context = f"Assignment: {assignment_description}\n\nUser's Code:\n{code}"
            else:
                context = f"User's Code:\n{code}"

            # Create a minimal file structure for the test generation prompt
            file_dict = {
                'filename': filename,
                'purpose': 'User-provided implementation',
                'code': code
            }

            prompt = get_test_generation_prompt(context, [file_dict], language)

            # Try to generate test cases with retries
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Test generation attempt {attempt + 1}/{self.max_retries}")
                    response_text = self.client.generate_response(prompt, max_tokens=2500)

                    logger.info(f"Received response (length: {len(response_text)} chars)")

                    # Extract JSON array from response
                    test_data = extract_json_from_response(response_text)

                    # If response is a dict with 'tests' key, extract it
                    if isinstance(test_data, dict) and 'tests' in test_data:
                        test_data = test_data['tests']

                    # Ensure it's a list
                    if not isinstance(test_data, list):
                        raise ValueError(f"Test data must be a list, got {type(test_data)}")

                    # Validate and create TestCase objects
                    test_cases = []
                    for idx, test in enumerate(test_data):
                        try:
                            test_case = TestCase(**test)
                            test_cases.append(test_case)
                        except Exception as e:
                            logger.warning(f"Skipping invalid test case {idx}: {e}")
                            continue

                    logger.info("=" * 80)
                    logger.info(f"✓ Successfully generated {len(test_cases)} test cases from user code")
                    logger.info("=" * 80)
                    return test_cases

                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    logger.warning(f"Test generation attempt {attempt + 1} failed: {str(e)}")

                    if attempt < self.max_retries - 1:
                        prompt += f"\n\nIMPORTANT: Previous attempt failed. Ensure your response is ONLY a valid JSON array starting with [ and ending with ]."
                    continue

            logger.error("=" * 80)
            logger.error(f"✗ FAILED to generate test cases after all retries")
            logger.error("=" * 80)
            return []

        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"✗ UNEXPECTED ERROR generating test cases: {str(e)}")
            logger.error("=" * 80)
            return []

parser_agent = None

def get_parser_agent() -> ParserAgent:
    global parser_agent
    if parser_agent is None:
        parser_agent = ParserAgent()
    return parser_agent
