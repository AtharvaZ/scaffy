import json
import re

def extract_json_from_response(response_text: str) -> dict:
    # Remove markdown code blocks if present
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    
    # Try to find JSON object in response
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    
    if start != -1 and end > start:
        json_str = response_text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}")
    else:
        raise ValueError("No JSON object found in response")


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