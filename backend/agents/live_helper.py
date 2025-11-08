"""Agent 3 for live helper tasks.
Provides contextual hints to students while they code
"""

from pyd_models.schemas import HintResponseSchema, HintSchema
from services import get_anthropic_client
from utils.agent_prompts import get_helper_prompt
from utils.json_parser import extract_json_from_response

# Agent responsible for providing live coding hints
class LiveHelperAgent:
    
    def __init__(self):
        self.client = get_anthropic_client()

    def provide_hint(self, inputData: HintResponseSchema) -> HintSchema:
        prompt = get_helper_prompt(
            task_description=inputData.task_description,
            concepts=inputData.concepts,
            student_code=inputData.student_code,
            question=inputData.question,
            previous_hints=inputData.previous_hints,
            help_count=inputData.help_count,
            known_language=inputData.known_language,
            target_language=inputData.target_language
        )

        response_text = self.client.generate_response(prompt, max_tokens=1500)

        data = extract_json_from_response(response_text)

        requirements = ["hint", "hint_type"]
        for req in requirements:
            if req not in data:
                raise ValueError(f"Missing required field '{req}' in the response data.")
            
        if "example_code" not in data:
            data["example_code"] = None

        return HintSchema(**data)
    
live_helper_agent = None
def get_live_helper_agent() -> LiveHelperAgent:
    global live_helper_agent
    if live_helper_agent is None:
        live_helper_agent = LiveHelperAgent()
    return live_helper_agent