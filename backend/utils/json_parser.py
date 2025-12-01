import json
import re
import logging

logger = logging.getLogger(__name__)

def extract_json_from_response(response_text: str) -> dict:
    """
    Robustly extract JSON from LLM response, handling:
    - Markdown code blocks
    - Truncated responses
    - Unescaped newlines in strings
    - Partial JSON objects
    """
    logger.info(f"Extracting JSON from response (length: {len(response_text)})")
    
    # Step 1: Clean markdown if present
    cleaned = _remove_markdown(response_text)
    
    # Step 2: Try direct parsing
    result = _try_direct_parse(cleaned)
    if result:
        return result
    
    # Step 3: Try to fix and parse
    fixed = _fix_json_issues(cleaned)
    if fixed != cleaned:
        result = _try_direct_parse(fixed)
        if result:
            return result
    
    # Step 4: Extract and fix JSON object
    json_obj = _extract_and_fix_json(response_text)
    if json_obj:
        return json_obj
    
    # Step 5: Handle truncated responses
    if _is_truncated(response_text):
        completed = _complete_truncated_json(response_text)
        result = _try_direct_parse(completed)
        if result:
            logger.info("Successfully parsed after completing truncated JSON")
            return result
    
    # Step 6: Last resort - find any valid JSON
    result = _find_any_valid_json(response_text)
    if result:
        return result
    
    # Failed to extract JSON
    logger.error(f"Could not extract valid JSON. First 500 chars: {response_text[:500]}")
    raise ValueError("Could not extract valid JSON from AI response.")


def _remove_markdown(text: str) -> str:
    """Remove markdown code block markers"""
    cleaned = text.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned)
    return cleaned


def _try_direct_parse(text: str) -> dict | None:
    """Try to parse JSON directly"""
    try:
        result = json.loads(text)
        logger.info(f"Successfully parsed JSON with keys: {list(result.keys())}")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Direct parse failed: {e}")
        return None


def _fix_json_issues(json_str: str) -> str:
    """
    Fix common JSON issues, especially unescaped newlines in strings.
    Specifically handles code_snippet and similar fields with multi-line content.
    """
    # Pattern to find string values that likely contain unescaped newlines
    # This is complex because we need to handle nested quotes and actual newlines
    
    # Step 1: Find potential problem areas (string values that span multiple lines)
    lines = json_str.split('\n')
    fixed_lines = []
    in_string = False
    string_start_pattern = re.compile(r'"(code_snippet|code|file_content|content)"\s*:\s*"')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a multi-line string value
        if string_start_pattern.search(line) and not line.rstrip().endswith('",') and not line.rstrip().endswith('"}'):
            # This might be the start of a multi-line string
            fixed_line = line
            in_string = True
            
            # Collect all lines until we find the closing quote
            j = i + 1
            accumulated_content = []
            
            while j < len(lines) and in_string:
                next_line = lines[j]

                # Check for the end of the string value (be more flexible with detection)
                # Look for patterns like: sometext", or sometext"}
                stripped = next_line.strip()
                ends_string = (
                    stripped.endswith('",') or
                    stripped.endswith('"}') or
                    stripped == '",' or
                    stripped == '"}' or
                    (stripped.endswith('"') and (j == len(lines) - 1 or '{' in lines[j+1] or '}' in lines[j+1]))
                )

                if ends_string:
                    # Found the end
                    in_string = False
                    # Add escaped content
                    if accumulated_content:
                        escaped_content = '\\n'.join(accumulated_content)
                        # Append the escaped content and the closing part
                        fixed_line = fixed_line + escaped_content + next_line.strip()
                    else:
                        fixed_line += next_line.strip()
                else:
                    # Still inside the string, accumulate and escape the content
                    # Escape backslashes first, then quotes
                    escaped_line = next_line.replace('\\', '\\\\').replace('"', '\\"')
                    accumulated_content.append(escaped_line)
                    j += 1
            
            fixed_lines.append(fixed_line)
            i = j + 1
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)


def _extract_and_fix_json(text: str) -> dict | None:
    """Extract JSON object and fix common issues"""
    # Find the first { and last }
    start = text.find('{')
    if start == -1:
        return None
    
    # Try to find matching closing brace
    brace_count = 0
    end = -1
    in_string = False
    escape_next = False
    
    for i in range(start, len(text)):
        char = text[i]
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i
                    break
    
    if end == -1:
        # No matching closing brace found, might be truncated
        logger.warning("No matching closing brace found, attempting to complete JSON")
        return _complete_and_parse_truncated(text[start:])
    
    json_str = text[start:end+1]
    
    # Try to fix and parse
    fixed = _fix_json_issues(json_str)
    return _try_direct_parse(fixed)


def _is_truncated(text: str) -> bool:
    """Check if the response appears to be truncated"""
    # Signs of truncation:
    # 1. Doesn't end with } or ]
    # 2. Has unclosed quotes
    # 3. Has unmatched braces
    
    trimmed = text.rstrip()
    if not trimmed.endswith('}') and not trimmed.endswith(']'):
        return True
    
    # Count braces
    open_braces = text.count('{')
    close_braces = text.count('}')
    if open_braces != close_braces:
        return True
    
    return False


def _complete_truncated_json(text: str) -> str:
    """
    Attempt to complete a truncated JSON response.
    This is specifically for handling cases where the AI hit the token limit.
    """
    # Find where the JSON likely got cut off
    # Common truncation points:
    # 1. In the middle of a string value
    # 2. In the middle of an array
    # 3. Missing closing braces/brackets
    
    # Start by finding all open structures
    open_braces = text.count('{')
    close_braces = text.count('}')
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    
    # Check if we're in the middle of a string
    quote_count = 0
    escape_next = False
    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == '\\':
            escape_next = True
            continue
        if char == '"':
            quote_count += 1
    
    in_string = quote_count % 2 == 1
    
    completed = text
    
    # If in a string, close it
    if in_string:
        completed += '"'
    
    # Close any open arrays
    for _ in range(open_brackets - close_brackets):
        completed += ']'
    
    # Close any open objects
    for _ in range(open_braces - close_braces):
        completed += '}'
    
    return completed


def _complete_and_parse_truncated(json_str: str) -> dict | None:
    """Complete a truncated JSON object and try to parse it"""
    # For truncated responses, we need to intelligently complete the JSON
    # This is especially important for code_snippet fields that often get cut off
    
    # Try to identify where we are in the JSON structure
    if '"code_snippet"' in json_str or '"file_content"' in json_str:
        # We're dealing with a code file that got truncated
        # Find the last sensible stopping point
        
        # Option 1: Close the string and add minimal structure
        if not json_str.rstrip().endswith('"}'):
            # We need to close the string and object
            completed = json_str
            
            # Check if we're in the middle of a string value
            # Count unescaped quotes to determine if we're inside a string
            in_string = False
            escape_next = False
            for char in json_str:
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"':
                    in_string = not in_string

            if in_string:
                # We're in a string, close it properly
                logger.info("Truncated inside a string, adding closing quote")
                completed += '",\n'
            
            # Add task_todos if missing (CRITICAL for data files)
            if '"task_todos"' not in json_str:
                logger.info("Adding missing task_todos to truncated response")
                completed += '  "task_todos": {"1": ["Review and customize the file content", "Test the file format"]}\n'

            # Close the object
            completed += '}'

            logger.info(f"Completed truncated JSON (length: {len(completed)})")
            result = _try_direct_parse(completed)
            if result:
                logger.info(f"Successfully parsed completed JSON with keys: {list(result.keys())}")
            return result
    
    return None


def _find_any_valid_json(text: str) -> dict | None:
    """Last resort: find any valid JSON object in the text"""
    # Try to find JSON objects starting from each {
    starts = [i for i, char in enumerate(text) if char == '{']
    
    for start in starts:
        # Try progressively longer substrings
        for end in range(start + 2, len(text) + 1):
            if text[end-1] == '}':
                try:
                    substring = text[start:end]
                    result = json.loads(substring)
                    if isinstance(result, dict):
                        logger.info(f"Found valid JSON object at positions {start}:{end}")
                        return result
                except json.JSONDecodeError:
                    continue
    
    return None


def validate_task_breakdown(data: dict) -> bool:
    """
    Validate task breakdown structure with improved error messages
    """
    # Check top-level required fields
    required_fields = ["overview", "total_estimated_time", "files"]
    for field in required_fields:
        if field not in data:
            # Try to provide a sensible default
            if field == "overview":
                data["overview"] = "Assignment tasks to complete"
            elif field == "total_estimated_time":
                data["total_estimated_time"] = "2 hours"
            elif field == "files":
                raise ValueError(f"Missing required field: {field}")
    
    # Validate files structure
    if not isinstance(data.get("files"), list) or len(data["files"]) == 0:
        raise ValueError("Files must be a non-empty list")

    # Validate each file
    for file_obj in data["files"]:
        filename = file_obj.get("filename", "unknown")

        # Check required file fields
        if "filename" not in file_obj or "purpose" not in file_obj:
            raise ValueError(f"File missing required field: filename or purpose")

        # File must have EITHER tasks OR classes, not both
        has_tasks = "tasks" in file_obj and file_obj["tasks"] is not None and len(file_obj["tasks"]) > 0
        has_classes = "classes" in file_obj and file_obj["classes"] is not None and len(file_obj["classes"]) > 0

        if has_tasks and has_classes:
            raise ValueError(f"File '{filename}' has both 'tasks' and 'classes' - must have only one")

        if not has_tasks and not has_classes:
            raise ValueError(f"File '{filename}' has neither 'tasks' nor 'classes' - all files must have at least one task or class")

        # Validate simple file structure (tasks directly in file)
        if has_tasks:
            task_ids = set()
            for task in file_obj["tasks"]:
                # Validate task ID
                task_id = task.get("id")
                if not isinstance(task_id, int):
                    raise ValueError(f"Task in '{filename}' has non-integer ID: {task_id}")
                if task_id in task_ids:
                    raise ValueError(f"Duplicate task ID {task_id} in '{filename}'")
                task_ids.add(task_id)

                # Validate dependencies are integers
                deps = task.get("dependencies", [])
                if not isinstance(deps, list):
                    raise ValueError(f"Task {task_id} in '{filename}' has invalid dependencies")
                for dep in deps:
                    if not isinstance(dep, int):
                        raise ValueError(f"Task {task_id} in '{filename}' has non-integer dependency: {dep}")

        # Validate multi-class file structure
        if has_classes:
            all_task_ids = set()
            for class_obj in file_obj["classes"]:
                if not isinstance(class_obj.get("tasks"), list) or len(class_obj["tasks"]) == 0:
                    raise ValueError(f"Class '{class_obj.get('class_name')}' in '{filename}' must have non-empty tasks list")

                for task in class_obj["tasks"]:
                    task_id = task.get("id")
                    if not isinstance(task_id, int):
                        raise ValueError(f"Task in class '{class_obj.get('class_name')}' has non-integer ID: {task_id}")
                    if task_id in all_task_ids:
                        raise ValueError(f"Duplicate task ID {task_id} in '{filename}'")
                    all_task_ids.add(task_id)

                    deps = task.get("dependencies", [])
                    if not isinstance(deps, list):
                        raise ValueError(f"Task {task_id} has invalid dependencies")
                    for dep in deps:
                        if not isinstance(dep, int):
                            raise ValueError(f"Task {task_id} has non-integer dependency: {dep}")

    return True


# Helper function for debugging
def debug_json_structure(text: str) -> dict:
    """Analyze JSON structure for debugging purposes"""
    analysis = {
        "length": len(text),
        "starts_with_brace": text.strip().startswith('{'),
        "ends_with_brace": text.strip().endswith('}'),
        "open_braces": text.count('{'),
        "close_braces": text.count('}'),
        "open_brackets": text.count('['),
        "close_brackets": text.count(']'),
        "quotes": text.count('"'),
        "has_code_snippet": '"code_snippet"' in text,
        "has_task_todos": '"task_todos"' in text,
        "likely_truncated": False
    }
    
    # Check for truncation
    if analysis["open_braces"] != analysis["close_braces"]:
        analysis["likely_truncated"] = True
    
    # Find where truncation might have occurred
    if analysis["likely_truncated"]:
        last_200 = text[-200:]
        analysis["truncation_context"] = last_200
    
    return analysis