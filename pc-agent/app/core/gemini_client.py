"""Gemini AI client (legacy support)."""
import google.generativeai as genai
from app.core.config import settings
import structlog

logger = structlog.get_logger()

_model = None


def _get_model():
    """Get or create Gemini model instance."""
    global _model
    if _model is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise
    return _model


def ask_gemini(prompt: str) -> str:
    """
    Ask Gemini AI a question.
    
    Args:
        prompt: Question or prompt
        
    Returns:
        Response text
        
    Raises:
        ValueError: If API key not configured
        Exception: If API call fails
    """
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise
