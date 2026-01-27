"""
Entry point for the I-Mart Voice Agent.
"""

import logging
import sys

import uvicorn

from src.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main():
    """Run the voice agent server."""
    logger.info(f"Starting I-Mart Voice Agent on {settings.HOST}:{settings.PORT}")
    logger.info(f"I-Mart API URL: {settings.IMART_API_URL}")

    uvicorn.run(
        "src.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Disable in production
        log_level="info",
    )


if __name__ == "__main__":
    main()
