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
    # Look for patterns like { ... } with proper nesting
    start_positions = [i for i, char in enumerate(response_text) if char == '{']
    
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
    required_fields = ["overview", "total_estimated_time", "tasks"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["tasks"], list) or len(data["tasks"]) == 0:
        raise ValueError("Tasks must be a non-empty list")
    
    # Validate each task
    for task in data["tasks"]:
        task_fields = ["id", "title", "description", "dependencies", "estimated_time", "concepts"]
        for field in task_fields:
            if field not in task:
                raise ValueError(f"Task missing required field: {field}")
    
    return True
