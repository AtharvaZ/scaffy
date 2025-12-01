""" Agent 2 for boiler plate code generation tasks.
Generates starter code templates with TODO comments for specific tasks
"""

import logging
from typing import List
from pyd_models.schemas import BoilerPlateCodeSchema, StarterCode
from services import get_anthropic_client
from utils.json_parser import extract_json_from_response

logger = logging.getLogger(__name__)

#validation function to check for duplication
def validate_no_duplication(code_snippet: str, class_names: list) -> bool:
    """Check if classes are duplicated in the generated code"""
    if not class_names:
        return True  # No classes to check

    for class_name in class_names:
        # Check for class declarations (handles different language syntaxes)
        patterns = [
            f"class {class_name}",  # Python, C#, Java
            f"public class {class_name}",  # C#, Java
            f"private class {class_name}",  # C#, Java
            f"protected class {class_name}",  # C#, Java
        ]

        total_count = 0
        matched_patterns = []
        for pattern in patterns:
            count = code_snippet.count(pattern)
            if count > 0:
                matched_patterns.append(f"{pattern} ({count}x)")
                total_count += count

        if total_count > 1:
            logger.error(f"Class {class_name} appears {total_count} times - DUPLICATION DETECTED!")
            logger.error(f"Matched patterns: {', '.join(matched_patterns)}")
            # Find line numbers where class appears
            lines = code_snippet.split('\n')
            for i, line in enumerate(lines, 1):
                if any(pattern in line for pattern in patterns):
                    logger.error(f"  Line {i}: {line.strip()}")
            return False
    
    # Also check for namespace/package duplication
    namespace_count = code_snippet.count("namespace ConsoleApp1")
    if namespace_count > 1:
        logger.error(f"Namespace duplicated {namespace_count} times!")
        return False
    
    return True

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
        Handles both code files and data files appropriately.
        """
        if not tasks:
            raise ValueError(f"No tasks provided for {filename}")

        # Detect if this is a non-code file (data/config/build files)
        # These should contain actual content, not code to generate them
        non_code_extensions = [
            '.xml', '.xsd', '.json', '.yaml', '.yml', '.toml',  # Data/config
            '.txt', '.csv', '.md',  # Text/documentation
            '.html', '.css', '.sql',  # Web/database
            '.sh', '.bat', '.ps1',  # Shell scripts (treated as config)
            '.dockerfile', '.dockerignore',  # Docker
            '.gitignore', '.gitattributes',  # Git
            '.env', '.properties', '.ini', '.cfg'  # Config files
        ]

        # Special files without extensions (case-insensitive)
        special_filenames = ['makefile', 'dockerfile', 'rakefile', 'gemfile', 'procfile', 'vagrantfile', 'cmakelists.txt']

        is_non_code_file = (
            any(filename.lower().endswith(ext) for ext in non_code_extensions) or
            filename.lower() in special_filenames or
            filename.lower().startswith('makefile')  # Makefile.inc, Makefile.am, etc.
        )

        # Convert tasks to dict format
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

        # Use different prompt for non-code files vs code files
        from utils.agent_prompts import get_file_codegen_prompt, get_non_code_file_prompt
        if is_non_code_file:
            prompt = get_non_code_file_prompt(tasks_dict_list, filename)
        else:
            prompt = get_file_codegen_prompt(
                tasks_dict_list,
                filename,
                class_structure=class_structure,
                template_variables=template_variables,
                method_signatures_by_class=method_signatures_by_class
            )

        # Smart token allocation for new compact format
        # New format: ONE code_snippet + task_todos dict (much more compact!)
        base_tokens = 1000  # Increased base for file scaffolding
        per_task = 100  # Reduced - we only need todos, not full code per task
        per_class = 400 if class_structure else 0

        estimated_tokens = base_tokens + (len(tasks) * per_task)
        if class_structure:
            estimated_tokens += len(class_structure) * per_class

        max_tokens = min(estimated_tokens, 8000)  # Increased cap for complex files
        logger.info(f"Using {max_tokens} tokens for {len(tasks)} tasks in {filename}")

        # ADD THIS: Extra instruction for complex files
        if len(tasks) > 5 or (class_structure and len(class_structure) > 2):
            prompt += "\n\nCRITICAL: Generate ONE complete file. Each class should appear EXACTLY ONCE. NO duplication."

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"File codegen for {filename}, attempt {attempt + 1}/{self.max_retries}")

                response_text = self.client.generate_response(prompt, max_tokens=max_tokens)

                # Log response for debugging
                logger.info(f"AI response preview (first 500 chars): {response_text[:500]}")
                logger.info(f"AI response last 200 chars: {response_text[-200:]}")
                logger.info(f"Total response length: {len(response_text)} characters")

                data = extract_json_from_response(response_text)
                logger.info(f"Extracted keys: {list(data.keys())}")

                # New format: {"code_snippet": "...", "task_todos": {"1": [...], "2": [...]}}
                if "code_snippet" in data and "task_todos" in data:
                    code = data["code_snippet"]
                    task_todos = data["task_todos"]

                    # Validate no class duplication
                    if class_structure:
                        if not validate_no_duplication(code, list(class_structure.keys())):
                            # Log the problematic code for debugging
                            logger.error("=" * 80)
                            logger.error("DUPLICATION DETECTED - Dumping code_snippet for analysis:")
                            logger.error(f"Code length: {len(code)} chars")
                            logger.error("First 2000 chars:")
                            logger.error(code[:2000])
                            logger.error("=" * 80)
                            raise ValueError("Class duplication detected")

                    # Expand into N task objects
                    results = []
                    for i, task in enumerate(tasks, 1):
                        results.append(StarterCode(
                            code_snippet=code,  # Same for all
                            instructions=f"Task {i}: {task.task_description}",
                            todos=task_todos.get(str(i), []),
                            concept_examples=None,
                            filename=filename
                        ))

                    logger.info(f"Expanded to {len(results)} tasks")
                    return results

                raise ValueError("Missing code_snippet or task_todos")

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    continue

        logger.error(f"All {self.max_retries} attempts failed for {filename}")
        raise ValueError(f"Failed to generate scaffolding for {filename}: {str(last_error)}")


codegen_agent = None
def get_batch_codegen_agent() -> CodegenAgent:
    global codegen_agent
    if codegen_agent is None:
        codegen_agent = CodegenAgent()
    return codegen_agent