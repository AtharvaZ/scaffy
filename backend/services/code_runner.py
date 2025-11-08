"""
Simple code execution service
Runs Python and JavaScript code with basic safety measures
"""

import subprocess
import tempfile
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CodeRunner:
    def __init__(self):
        self.timeout = 5  # 5 second timeout
        self.max_output_length = 10000  # Limit output to prevent memory issues
    
    def run_python(self, code: str) -> Dict[str, Any]:
        """Run Python code and return results"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Run the code
                result = subprocess.run(
                    ['python3', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                # Get output
                stdout = result.stdout[:self.max_output_length] if result.stdout else ""
                stderr = result.stderr[:self.max_output_length] if result.stderr else ""
                
                return {
                    "success": result.returncode == 0,
                    "output": stdout,
                    "error": stderr,
                    "exit_code": result.returncode,
                    "execution_time": "< 5s"
                }
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {self.timeout} seconds. Your code might have an infinite loop.",
                "exit_code": -1,
                "execution_time": f"> {self.timeout}s"
            }
        except Exception as e:
            logger.error(f"Error running Python code: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "exit_code": -1,
                "execution_time": "error"
            }
    
    def run_javascript(self, code: str) -> Dict[str, Any]:
        """Run JavaScript code using Node.js"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Run the code with Node.js
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                # Get output
                stdout = result.stdout[:self.max_output_length] if result.stdout else ""
                stderr = result.stderr[:self.max_output_length] if result.stderr else ""
                
                return {
                    "success": result.returncode == 0,
                    "output": stdout,
                    "error": stderr,
                    "exit_code": result.returncode,
                    "execution_time": "< 5s"
                }
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {self.timeout} seconds. Your code might have an infinite loop.",
                "exit_code": -1,
                "execution_time": f"> {self.timeout}s"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "output": "",
                "error": "Node.js is not installed. JavaScript execution requires Node.js to be installed on the server.",
                "exit_code": -1,
                "execution_time": "error"
            }
        except Exception as e:
            logger.error(f"Error running JavaScript code: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "exit_code": -1,
                "execution_time": "error"
            }
    
    def run_code(self, code: str, language: str) -> Dict[str, Any]:
        """Run code based on language"""
        language = language.lower()
        
        if language == 'python':
            return self.run_python(code)
        elif language in ['javascript', 'js']:
            return self.run_javascript(code)
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Language '{language}' is not supported. Supported languages: Python, JavaScript",
                "exit_code": -1,
                "execution_time": "0s"
            }


# Singleton instance
_code_runner = None

def get_code_runner() -> CodeRunner:
    """Get the code runner singleton"""
    global _code_runner
    if _code_runner is None:
        _code_runner = CodeRunner()
    return _code_runner

