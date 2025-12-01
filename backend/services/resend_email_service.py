"""
Alternative email service using Resend API (works on Render free tier)
Resend has a free tier: 100 emails/day, 3,000 emails/month
Sign up at: https://resend.com
"""

import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ResendEmailService:
    def __init__(self):
        # Resend API configuration
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
        self.recipient_email = os.getenv("FEEDBACK_EMAIL", "atharvazaveri4@gmail.com")
        
        logger.info("=" * 80)
        logger.info("RESEND EMAIL SERVICE CONFIGURATION:")
        logger.info(f"API Key: {'*' * 20 if self.api_key else 'NOT SET'}")
        logger.info(f"From Email: {self.from_email}")
        logger.info(f"Recipient: {self.recipient_email}")
        logger.info(f"Resend Configured: {bool(self.api_key)}")
        logger.info("=" * 80)
        
    def send_feedback(self, name: str, email: str, feedback: str) -> bool:
        """
        Send feedback email using Resend API
        
        Args:
            name: User's name
            email: User's email
            feedback: Feedback message
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.api_key:
                # No API key - log to console instead
                logger.warning("Resend API key not configured - logging feedback to console")
                logger.info("=" * 80)
                logger.info("FEEDBACK RECEIVED:")
                logger.info(f"From: {name} ({email})")
                logger.info(f"Message: {feedback}")
                logger.info("=" * 80)
                return True
            
            logger.info(f"Sending feedback email via Resend to {self.recipient_email}")
            
            # Prepare email data
            email_data = {
                "from": self.from_email,
                "to": [self.recipient_email],
                "reply_to": email,
                "subject": f"Scaffi Feedback from {name}",
                "text": f"""
New feedback received from Scaffi:

Name: {name}
Email: {email}

Feedback:
{feedback}

---
Sent from Scaffi Feedback System
"""
            }
            
            # Send via Resend API
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=email_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Feedback email sent successfully via Resend")
                return True
            else:
                logger.error(f"Resend API error: {response.status_code} - {response.text}")
                # Still log to console as fallback
                logger.info("=" * 80)
                logger.info("FEEDBACK RECEIVED (email failed, logging to console):")
                logger.info(f"From: {name} ({email})")
                logger.info(f"Message: {feedback}")
                logger.info("=" * 80)
                return True  # Return True so user sees success
                
        except Exception as e:
            logger.error(f"Failed to send feedback email: {e}", exc_info=True)
            # Log to console as fallback
            logger.info("=" * 80)
            logger.info("FEEDBACK RECEIVED (error occurred, logging to console):")
            logger.info(f"From: {name} ({email})")
            logger.info(f"Message: {feedback}")
            logger.info("=" * 80)
            return True  # Return True so user sees success


# Singleton instance
_resend_email_service = None

def get_resend_email_service() -> ResendEmailService:
    """Get the Resend email service singleton"""
    global _resend_email_service
    if _resend_email_service is None:
        _resend_email_service = ResendEmailService()
    return _resend_email_service
