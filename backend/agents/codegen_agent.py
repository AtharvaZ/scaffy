""" Agent 2 for boiler plate code generation tasks.
Generates starter code templates with TODO comments for specific tasks
"""

from pyd_models.schemas import BoilerPlateCodeSchema, StarterCode
from services import get_anthropic_client
from utils.agent_prompts import get_codegen_prompt
from utils.json_parser import extract_json_from_response

# Agent responsible for generating boilerplate code templates
class CodegenAgent:

    def __init__(self):
        self.client = get_anthropic_client()

    def generate_boilerplate_code(self, inputData: BoilerPlateCodeSchema) -> StarterCode:
        prompt = get_codegen_prompt(
            task_description=inputData.task_description,
            language=inputData.programming_language,
            concepts=inputData.concepts,
            known_language=inputData.known_language
        )

        response_text = self.client.generate_response(prompt, max_tokens=2500)

        data = extract_json_from_response(response_text)

        requirements = ["code", "instructions", "todos"]
        for req in requirements:
            if req not in data:
                raise ValueError(f"Missing required field '{req}' in the response data.")
            
        if "concept_examples" not in data:
            data["concept_examples"] = None

        return StarterCode(**data)

codegen_agent = None
def get_codegen_agent() -> CodegenAgent:
    global codegen_agent
    if codegen_agent is None:
        codegen_agent = CodegenAgent()
    return codegen_agent