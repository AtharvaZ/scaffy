import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


class AnthropicClient:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    # Generate response from Anthropic Claude model
    def generate_response(self, prompt: str, max_tokens: int=4000) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages = [{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    

_client_instance = None

#Get or Create Anthropic Client Singleton
def get_anthropic_client() -> AnthropicClient:
   global _client_instance
   if _client_instance is None:
         _client_instance = AnthropicClient()
   return _client_instance