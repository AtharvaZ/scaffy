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
        self.timeout = 30  # 30 second timeout (increased for complex programs with threading)
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
    
    def _check_output_match(self, actual_output: str, expected_output: str) -> bool:
        """
        Check if actual output matches expected output with support for special patterns.

        Patterns:
        - "CONTAINS:word1,word2,word3" → Check if output contains all words/phrases
        - "COUNT:pattern:N" → Check if pattern appears exactly N times
        - Regular string → Exact match (after stripping whitespace)

        Args:
            actual_output: Actual program output
            expected_output: Expected output or pattern

        Returns:
            True if outputs match, False otherwise
        """
        expected = expected_output.strip()
        actual = actual_output.strip()

        # Pattern 1: CONTAINS check
        if expected.startswith("CONTAINS:"):
            patterns = expected[9:].split(",")  # Remove "CONTAINS:" prefix
            # All patterns must be in output
            return all(pattern.strip() in actual for pattern in patterns)

        # Pattern 2: COUNT check
        if expected.startswith("COUNT:"):
            parts = expected[6:].split(":")  # Remove "COUNT:" prefix
            if len(parts) == 2:
                pattern, count_str = parts
                try:
                    expected_count = int(count_str.strip())
                    actual_count = actual.count(pattern.strip())
                    return actual_count == expected_count
                except ValueError:
                    logger.warning(f"Invalid COUNT pattern: {expected}")
                    return False

        # Default: Exact match
        return actual == expected

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
                    elif language.lower() in ['csharp', 'c#', 'cs']:
                        # For C#, check if code already has Main method
                        has_main = 'static void Main' in code or 'static async Task Main' in code

                        if function_name.lower() == 'main' and has_main:
                            # Integration test - code already has Main, just run it
                            test_code = code
                        elif function_name.lower() == 'main' and not has_main:
                            # Need to add Main method to call the function
                            test_code = f"""{code}

// Test execution
class TestRunner {{
    static void Main(string[] args) {{
        {function_name}({input_data});
    }}
}}"""
                        elif '.' in function_name:
                            # Method test with namespace/class qualification (e.g., Namespace.ClassName.MethodName or ClassName.MethodName)
                            parts = function_name.split('.')

                            if len(parts) == 3:
                                # Namespace.ClassName.MethodName format
                                namespace_name, class_name, method_name = parts
                                full_class_name = f"{namespace_name}.{class_name}"
                            elif len(parts) == 2:
                                # ClassName.MethodName format
                                class_name, method_name = parts
                                full_class_name = class_name
                            else:
                                # Fallback for unexpected format
                                full_class_name = parts[0]
                                method_name = parts[-1]

                            if has_main:
                                # Code has Main, need to call method from outside the namespace
                                # Remove the existing Main and add test Main outside namespace
                                # This is complex, so for integration tests just run the code
                                test_code = code
                            else:
                                # No Main exists, add TestRunner outside the namespace
                                test_code = f"""{code}

// Test execution
class TestRunner {{
    static void Main(string[] args) {{
        var instance = new {full_class_name}();
        var result = instance.{method_name}({input_data});
        Console.WriteLine(result);
    }}
}}"""
                        else:
                            # Simple function name without dots
                            if has_main:
                                # Already has Main, just run it
                                test_code = code
                            else:
                                # Add Main to call the function
                                test_code = f"""{code}

// Test execution
class TestRunner {{
    static void Main(string[] args) {{
        var result = {function_name}({input_data});
        Console.WriteLine(result);
    }}
}}"""
                    elif language.lower() in ['java']:
                        # For Java, handle integration tests vs function tests
                        if function_name.lower() == 'main':
                            # Integration test - run the whole program
                            test_code = code
                        else:
                            # Function test
                            if '.' in function_name:
                                class_name, method_name = function_name.split('.', 1)
                                test_code = f"""{code}

// Test execution
class TestRunner {{
    public static void main(String[] args) {{
        {class_name} instance = new {class_name}();
        var result = instance.{method_name}({input_data});
        System.out.println(result);
    }}
}}"""
                            else:
                                test_code = f"""{code}

// Test execution
class TestRunner {{
    public static void main(String[] args) {{
        var result = {function_name}({input_data});
        System.out.println(result);
    }}
}}"""
                    else:
                        # For other languages, try a generic approach
                        test_code = f"{code}\n\n{function_name}({input_data});"

                    # Run the test
                    result = self.run_code(test_code, language, stdin="")

                    # Get actual output and clean it
                    actual_output = result.get('output', '').strip()

                    # Check if test passed (compare outputs with special pattern matching)
                    passed = self._check_output_match(actual_output, expected_output)

                    if passed:
                        tests_passed += 1
                    else:
                        tests_failed += 1

                    # Create test result
                    test_result = TestResult(
                        test_name=test_name,
                        function_name=function_name,  # Add function name
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
                        function_name=test_case.get('function_name', 'Unknown'),  # Add function name
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
