import anthropic
import os
import time
import logging
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1  # Start with 1 second delay
        self.max_delay = 60  # Max 60 seconds between retries

    def generate_response(self, prompt: str, max_tokens: int = 4000, model: str = None) -> str:
        """
        Generate response with retry logic and exponential backoff.
        Handles 529 (Overloaded) and other retryable errors.
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Use provided model or fall back to instance default
                model_to_use = model or self.model
                logger.info(f"API call attempt {attempt + 1}/{self.max_retries} using model: {model_to_use}")

                response = self.client.messages.create(
                    model=model_to_use,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                logger.info(f"API call succeeded on attempt {attempt + 1}")
                return response.content[0].text
                
            except anthropic.RateLimitError as e:
                last_exception = e
                logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_backoff(attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded")
                    
            except anthropic.APIError as e:
                # Handle 529 Overloaded and other API errors
                if hasattr(e, 'status_code') and e.status_code == 529:
                    last_exception = e
                    logger.warning(f"API overloaded (529) on attempt {attempt + 1}")
                    
                    if attempt < self.max_retries - 1:
                        delay = self._calculate_backoff(attempt)
                        logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Max retries ({self.max_retries}) exceeded")
                else:
                    # Non-retryable API error, raise immediately
                    logger.error(f"Non-retryable API error: {e}")
                    raise
                    
            except Exception as e:
                # Unexpected error, log and raise
                logger.error(f"Unexpected error during API call: {e}")
                raise
        
        # If we exhausted all retries, raise the last exception
        error_msg = f"Failed after {self.max_retries} attempts. Last error: {str(last_exception)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        Formula: base_delay * (2 ^ attempt) with jitter
        """
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        
        # Add jitter (randomness) to prevent thundering herd
        import random
        jitter = random.uniform(0, 0.1 * delay)
        
        return delay + jitter


_client_instances = {}

def get_anthropic_client(model: str = "claude-sonnet-4-20250514") -> AnthropicClient:
    """
    Get or Create Anthropic Client for specific model.
    Uses a separate client instance per model to avoid conflicts.
    """
    global _client_instances
    if model not in _client_instances:
        _client_instances[model] = AnthropicClient(model=model)
    return _client_instances[model]