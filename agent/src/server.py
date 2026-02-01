"""
FastAPI server for WebSocket audio streaming.
Handles bidirectional audio communication with voice agent.

This implementation follows the Pipecat reference architecture from websocket/server/server.py
"""

import asyncio
import logging

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.bot import run_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="I-Mart Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "voice-agent"}


@app.post("/connect")
async def bot_connect(request: Request):
    """
    RTVI-compatible connect endpoint.
    Returns WebSocket URL for client connection.

    This endpoint is called by PipecatClient to get the WebSocket URL.
    """
    ws_url = f"ws://{settings.HOST}:{settings.PORT}/ws"
    logger.info(f"Connect request, returning ws_url: {ws_url}")
    return {"ws_url": ws_url}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    RTVI-compatible WebSocket endpoint.

    Follows the reference implementation pattern:
    1. Accept the WebSocket connection
    2. Pass the raw websocket to run_bot
    3. run_bot creates the transport internally
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    try:
        await run_bot(websocket)
    except Exception as e:
        logger.error(f"Exception in run_bot: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on server shutdown."""
    logger.info("Shutting down voice agent server...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
    )
