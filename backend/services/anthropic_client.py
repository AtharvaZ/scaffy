import anthropic
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_retries = 5
        self.base_delay = 2  # Base delay in seconds

    # Generate response from Anthropic Claude model with retry logic for rate limits
    def generate_response(self, prompt: str, max_tokens: int=4000) -> str:
        """
        Generate response with retry logic for rate limiting and overload errors.
        Uses exponential backoff for retries.
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages = [{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            except anthropic.APIStatusError as e:
                # Handle 529 Overloaded errors, rate limits, and other API status errors
                error_str = str(e).lower()
                status_code = getattr(e, 'status_code', None)
                
                # Check for rate limit or overloaded errors (529, 429, or "overloaded" in message)
                is_rate_limit = status_code == 429 or "rate limit" in error_str
                is_overloaded = status_code == 529 or "overloaded" in error_str
                
                if is_rate_limit or is_overloaded:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        # Exponential backoff: 2s, 4s, 8s, 16s, 32s
                        delay = self.base_delay * (2 ** attempt)
                        error_type = "rate limit" if is_rate_limit else "overloaded"
                        logger.warning(f"API {error_type} error (attempt {attempt + 1}/{self.max_retries}). Retrying in {delay}s...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"API {error_type} error after {self.max_retries} attempts")
                        # Re-raise with a clearer message
                        raise Exception(f"API service is temporarily {'overloaded' if is_overloaded else 'rate limited'}. Please try again in a few moments.")
                else:
                    # For other API status errors, don't retry
                    raise
                    
            except Exception as e:
                # Check if it's a rate limit or overloaded error by message
                error_str = str(e).lower()
                if "rate limit" in error_str or "overloaded" in error_str or "529" in error_str:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt)
                        logger.warning(f"API error detected (attempt {attempt + 1}/{self.max_retries}). Retrying in {delay}s...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"API error after {self.max_retries} attempts")
                        raise Exception(f"API service is temporarily unavailable. Please try again in a few moments.")
                else:
                    # For other errors, don't retry
                    logger.error(f"Unexpected error in Anthropic API call: {str(e)}")
                    raise
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        else:
            raise Exception("Failed to generate response after retries")
    

_client_instance = None

#Get or Create Anthropic Client Singleton
def get_anthropic_client() -> AnthropicClient:
   global _client_instance
   if _client_instance is None:
         _client_instance = AnthropicClient()
   return _client_instance