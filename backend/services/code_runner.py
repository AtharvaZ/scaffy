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
            exit_code = run_result.get("code", 0)
            
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
