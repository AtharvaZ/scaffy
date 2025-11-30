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
        # Use Sonnet 4 for hints - best for nuanced educational guidance
        self.client = get_anthropic_client(model="claude-sonnet-4-20250514")
        self.max_retries = 3

    def provide_hint(self, inputData: HintResponseSchema) -> HintSchema:
        """
        Provide hint with retry logic for robust JSON extraction.
        Retries up to max_retries times if JSON parsing fails.
        NEW: Can analyze test results to help debug test cases when code is correct.
        """
        # Log test results info with detailed data
        if inputData.test_results:
            logger.info("=" * 80)
            logger.info(f"📊 TEST RESULTS RECEIVED: {len(inputData.test_results)} tests")

            # Correct test filtering logic
            passed = [t for t in inputData.test_results if t.get('passed') == True]
            failed = [t for t in inputData.test_results if t.get('passed') == False]

            logger.info(f"  ✓ Passed: {len(passed)}, ✗ Failed: {len(failed)}")

            # Log first 2 failed tests in detail
            if failed:
                logger.info("\n  FAILED TEST DETAILS:")
                for idx, test in enumerate(failed[:2], 1):
                    logger.info(f"    Test {idx}: {test.get('test_name', 'Unknown')}")
                    logger.info(f"      Function: {test.get('function_name', 'N/A')}")
                    logger.info(f"      Input: {test.get('input_data', 'N/A')}")
                    logger.info(f"      Expected: {test.get('expected_output', 'N/A')}")
                    logger.info(f"      Actual: {test.get('actual_output', 'N/A')}")
                    if test.get('error'):
                        logger.info(f"      Error: {test.get('error')}")
            logger.info("=" * 80)
        else:
            logger.info("📊 No test results provided")

        prompt = get_helper_prompt(
            task_description=inputData.task_description,
            concepts=inputData.concepts,
            student_code=inputData.student_code,
            question=inputData.question,
            previous_hints=inputData.previous_hints,
            help_count=inputData.help_count,
            known_language=inputData.known_language,
            target_language=inputData.target_language,
            experience_level=inputData.experience_level,
            test_results=inputData.test_results  # NEW: Pass test results for analysis
        )

        # Log if test results section is in prompt
        if inputData.test_results:
            if "TEST RESULTS:" in prompt:
                logger.info("✅ Test results section FOUND in prompt")
                # Log how many characters the test section is
                test_section_start = prompt.find("TEST RESULTS:")
                test_section_end = prompt.find("Student's Question:", test_section_start)
                if test_section_start != -1 and test_section_end != -1:
                    section_length = test_section_end - test_section_start
                    logger.info(f"   Test results section length: {section_length} chars")
            else:
                logger.warning("❌ Test results were provided but NOT FOUND in prompt!")

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

                # Log the hint for debugging (especially for test results cases)
                if inputData.test_results:
                    logger.info("=" * 80)
                    logger.info("🎯 GENERATED HINT (with test results):")
                    logger.info(f"   Hint Type: {data.get('hint_type', 'N/A')}")
                    logger.info(f"   Hint Preview: {data.get('hint', '')[:200]}...")
                    logger.info("=" * 80)

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