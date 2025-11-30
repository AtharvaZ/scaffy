import json
import re
import logging

logger = logging.getLogger(__name__)

def extract_json_from_response(response_text: str) -> dict:
    """
    Robustly extract JSON from LLM response, handling various formats:
    - Markdown code blocks (```json ... ```)
    - Plain JSON objects
    - Text before/after JSON
    - Nested braces in strings
    """
    # Log original response for debugging
    logger.debug(f"Extracting JSON from response (length: {len(response_text)})")
    
    # First, try to remove common markdown patterns
    # Remove ```json at start and ``` at end
    cleaned = response_text.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned)
    
    # Try to parse the cleaned text directly first (fastest path)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # If that didn't work, try to extract JSON object by finding matching braces
    # This handles cases where there's text before/after the JSON
    json_obj = _extract_json_object(response_text)
    if json_obj:
        return json_obj
    
    # Last resort: try to find any valid JSON in the response
    # IMPORTANT: Try from the BEGINNING first to get outermost object
    # This prevents extracting inner objects when the response is truncated
    start_positions = [i for i, char in enumerate(response_text) if char == '{']

    # Prioritize the first '{' (outermost object)
    for start in start_positions:
        # Try to find the matching closing brace
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start, len(response_text)):
            char = response_text[i]
            
            # Handle string escaping
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            
            # Track if we're inside a string (to ignore braces in strings)
            if char == '"':
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found matching closing brace
                        json_str = response_text[start:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            # This wasn't valid JSON, try next start position
                            break
    
    # If we still haven't found valid JSON, raise an error
    logger.error(f"Could not extract valid JSON from response. First 500 chars: {response_text[:500]}")
    raise ValueError(
        "Could not extract valid JSON from AI response. "
        "The AI may not have returned properly formatted JSON. "
        "Please try again or simplify your input."
    )


def _extract_json_object(text: str) -> dict | None:
    """Helper function to extract the first valid JSON object from text"""
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start != -1 and end > start:
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None


def validate_task_breakdown(data: dict) -> bool:
    """
    Validate task breakdown structure (UPDATED FOR MULTI-FILE AND MULTI-CLASS)
    """
    # Check top-level required fields
    required_fields = ["overview", "total_estimated_time", "files"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Check template_structure field (optional but should be present)
    if "template_structure" not in data:
        logger.warning("Missing 'template_structure' field - will use default")
        data["template_structure"] = {
            "has_template": False,
            "variable_names": [],
            "class_names": []
        }

    if not isinstance(data["files"], list) or len(data["files"]) == 0:
        raise ValueError("Files must be a non-empty list")

    # Validate each file
    for file_obj in data["files"]:
        filename = file_obj.get('filename', 'unknown')

        # Check required file fields
        if "filename" not in file_obj or "purpose" not in file_obj:
            raise ValueError(f"File missing required field: filename or purpose")

        # File must have EITHER tasks OR classes, not both or neither
        has_tasks = "tasks" in file_obj and file_obj["tasks"] is not None
        has_classes = "classes" in file_obj and file_obj["classes"] is not None

        if has_tasks and has_classes:
            raise ValueError(f"File '{filename}' has both 'tasks' and 'classes' - must have only one")

        if not has_tasks and not has_classes:
            raise ValueError(f"File '{filename}' has neither 'tasks' nor 'classes' - must have one")

        # Validate simple file structure (tasks directly in file)
        if has_tasks:
            if not isinstance(file_obj["tasks"], list) or len(file_obj["tasks"]) == 0:
                raise ValueError(f"File '{filename}' must have a non-empty tasks list")

            for task in file_obj["tasks"]:
                task_fields = ["id", "title", "description", "dependencies", "estimated_time", "concepts"]
                for field in task_fields:
                    if field not in task:
                        raise ValueError(f"Task in '{filename}' missing required field: {field}")

        # Validate tests if present (tests are now per-file)
        if "tests" in file_obj and file_obj["tests"] is not None:
            if not isinstance(file_obj["tests"], list):
                raise ValueError(f"File '{filename}' tests must be a list")
            logger.info(f"File '{filename}' has {len(file_obj['tests'])} tests")

        # Validate multi-class file structure (classes with tasks)
        if has_classes:
            if not isinstance(file_obj["classes"], list) or len(file_obj["classes"]) == 0:
                raise ValueError(f"File '{filename}' must have a non-empty classes list")

            for class_obj in file_obj["classes"]:
                if "class_name" not in class_obj or "purpose" not in class_obj or "tasks" not in class_obj:
                    raise ValueError(f"Class in '{filename}' missing required fields")

                if not isinstance(class_obj["tasks"], list) or len(class_obj["tasks"]) == 0:
                    raise ValueError(f"Class '{class_obj.get('class_name')}' in '{filename}' must have non-empty tasks list")

                for task in class_obj["tasks"]:
                    task_fields = ["id", "title", "description", "dependencies", "estimated_time", "concepts"]
                    for field in task_fields:
                        if field not in task:
                            raise ValueError(f"Task in class '{class_obj.get('class_name')}' missing field: {field}")

    return True
