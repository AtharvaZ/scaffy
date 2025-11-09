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
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1  # Start with 1 second delay
        self.max_delay = 60  # Max 60 seconds between retries

    def generate_response(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Generate response with retry logic and exponential backoff.
        Handles 529 (Overloaded) and other retryable errors.
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"API call attempt {attempt + 1}/{self.max_retries}")
                
                response = self.client.messages.create(
                    model=self.model,
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


_client_instance = None

def get_anthropic_client() -> AnthropicClient:
    """Get or Create Anthropic Client Singleton"""
    global _client_instance
    if _client_instance is None:
        _client_instance = AnthropicClient()
    return _client_instance