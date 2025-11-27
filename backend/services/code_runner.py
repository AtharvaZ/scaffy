"""
Code execution service using Piston API
Runs Python and JavaScript code with interactive input support
"""

import requests
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class CodeRunner:
    def __init__(self):
        # Use public Piston API or set your own instance URL via environment variable
        self.piston_api_url = os.getenv("PISTON_API_URL", "https://emkc.org/api/v2/piston")
        self.timeout = 10  # 10 second timeout
        self.max_output_length = 10000  # Limit output to prevent memory issues
        
        # Language mappings for Piston API
        self.language_map = {
            'python': 'python3',
            'javascript': 'javascript',
            'js': 'javascript',
            'java': 'java',
            'csharp': 'csharp',
            'c#': 'csharp',
            'cs': 'csharp',
            'c++': 'cpp',
            'c': 'c',
            'typescript': 'typescript'
        }
    
    def run_code(self, code: str, language: str, stdin: Optional[str] = None) -> Dict[str, Any]:
        """
        Run code using Piston API
        
        Args:
            code: Code to execute
            language: Programming language
            stdin: Optional stdin input (for input() calls). If None, provides default test values.
        
        Returns:
            Dict with success, output, error, exit_code, execution_time
        """
        language = language.lower()
        
        # Map language to Piston API language name
        piston_language = self.language_map.get(language)
        if not piston_language:
            return {
                "success": False,
                "output": "",
                "error": f"Language '{language}' is not supported. Supported languages: {', '.join(self.language_map.keys())}",
                "exit_code": -1,
                "execution_time": "0s"
            }
        
        # If no stdin provided, use default test values for input() calls
        # This allows code with input() to run without EOFError
        if stdin is None:
            # Provide multiple test inputs (one per line) for multiple input() calls
            # Common test values: numbers, strings, yes/no, exit commands
            stdin = "1234\ntest_input\ny\nyes\n1\n0\nx\n"
        
        try:
            # Prepare request payload
            payload = {
                "language": piston_language,
                "version": "*",  # Use latest version
                "files": [
                    {
                        "content": code
                    }
                ],
                "stdin": stdin,  # Provide stdin for input() calls
                "run_timeout": self.timeout * 1000  # Convert to milliseconds
            }
            
            logger.info(f"Executing {language} code via Piston API ({len(code)} characters)")
            
            # Make request to Piston API
            response = requests.post(
                f"{self.piston_api_url}/execute",
                json=payload,
                timeout=self.timeout + 5  # Add buffer for timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Piston API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "output": "",
                    "error": f"Code execution service error: {response.status_code}. Please try again later.",
                    "exit_code": -1,
                    "execution_time": "error"
                }
            
            result = response.json()
            
            # Extract output and error
            run_result = result.get("run", {})
            stdout = run_result.get("stdout", "")[:self.max_output_length]
            stderr = run_result.get("stderr", "")[:self.max_output_length]
            exit_code = run_result.get("code")

            # Ensure exit_code is always an integer
            if exit_code is None:
                exit_code = 1 if stderr else 0
            exit_code = int(exit_code)

            # Check if execution was successful
            success = exit_code == 0 and not stderr
            
            # Get execution time if available
            execution_time = run_result.get("time", "< 5s")
            if isinstance(execution_time, (int, float)):
                execution_time = f"{execution_time:.2f}s"
            
            logger.info(f"Execution completed: success={success}, exit_code={exit_code}")
            
            return {
                "success": success,
                "output": stdout,
                "error": stderr,
                "exit_code": exit_code,
                "execution_time": execution_time
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"Execution timed out after {self.timeout} seconds")
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {self.timeout} seconds. Your code might have an infinite loop.",
                "exit_code": -1,
                "execution_time": f"> {self.timeout}s"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Piston API request error: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Failed to connect to code execution service: {str(e)}. Please check your connection or try again later.",
                "exit_code": -1,
                "execution_time": "error"
            }
        except Exception as e:
            logger.error(f"Error running code via Piston API: {e}", exc_info=True)
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "exit_code": -1,
                "execution_time": "error"
            }

    def run_with_tests(self, code: str, language: str, test_cases: list) -> Dict[str, Any]:
        """
        Run code with test cases and return results

        Args:
            code: Student's code
            language: Programming language
            test_cases: List of test case dicts with function_name, input_data, expected_output

        Returns:
            Dict with test_results, tests_passed, tests_failed, plus regular execution info
        """
        try:
            from pyd_models.schemas import TestResult

            test_results = []
            tests_passed = 0
            tests_failed = 0

            logger.info(f"Running {len(test_cases)} test cases for {language} code")

            for test_case in test_cases:
                try:
                    test_name = test_case.get('test_name', 'Unknown Test')
                    function_name = test_case.get('function_name', '')
                    input_data = test_case.get('input_data', '')
                    expected_output = test_case.get('expected_output', '').strip()

                    # Generate test code based on language
                    if language.lower() == 'python':
                        test_code = f"{code}\n\n# Test execution\nresult = {function_name}({input_data})\nprint(result)"
                    elif language.lower() in ['javascript', 'js']:
                        test_code = f"{code}\n\n// Test execution\nconst result = {function_name}({input_data});\nconsole.log(result);"
                    else:
                        # For other languages, try a generic approach
                        test_code = f"{code}\n\n{function_name}({input_data});"

                    # Run the test
                    result = self.run_code(test_code, language, stdin="")

                    # Get actual output and clean it
                    actual_output = result.get('output', '').strip()

                    # Check if test passed (compare outputs as strings)
                    passed = actual_output == expected_output

                    if passed:
                        tests_passed += 1
                    else:
                        tests_failed += 1

                    # Create test result
                    test_result = TestResult(
                        test_name=test_name,
                        passed=passed,
                        input_data=input_data,
                        expected_output=expected_output,
                        actual_output=actual_output,
                        error=result.get('error') if result.get('error') else None
                    )
                    test_results.append(test_result)

                except Exception as e:
                    logger.error(f"Error running test case '{test_name}': {e}")
                    test_results.append(TestResult(
                        test_name=test_case.get('test_name', 'Unknown Test'),
                        passed=False,
                        input_data=test_case.get('input_data', ''),
                        expected_output=test_case.get('expected_output', ''),
                        actual_output='',
                        error=f"Test execution error: {str(e)}"
                    ))
                    tests_failed += 1

            # Also run the code normally to get any compilation/syntax errors
            normal_result = self.run_code(code, language, stdin="")

            return {
                "success": tests_passed > 0 and tests_failed == 0,
                "output": normal_result.get('output', ''),
                "error": normal_result.get('error', ''),
                "exit_code": normal_result.get('exit_code', 0),
                "execution_time": normal_result.get('execution_time', ''),
                "test_results": test_results,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed
            }

        except Exception as e:
            logger.error(f"Error in run_with_tests: {e}", exc_info=True)
            return {
                "success": False,
                "output": "",
                "error": f"Test execution error: {str(e)}",
                "exit_code": -1,
                "execution_time": "error",
                "test_results": [],
                "tests_passed": 0,
                "tests_failed": len(test_cases)
            }

    def run_python(self, code: str, stdin: Optional[str] = None) -> Dict[str, Any]:
        """Run Python code"""
        return self.run_code(code, "python", stdin)
    
    def run_javascript(self, code: str, stdin: Optional[str] = None) -> Dict[str, Any]:
        """Run JavaScript code"""
        return self.run_code(code, "javascript", stdin)


# Singleton instance
_code_runner = None

def get_code_runner() -> CodeRunner:
    """Get the code runner singleton"""
    global _code_runner
    if _code_runner is None:
        _code_runner = CodeRunner()
    return _code_runner
