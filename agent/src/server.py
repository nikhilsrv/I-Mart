"""
FastAPI server for WebRTC signaling.
Handles SDP offer/answer and ICE candidate exchange.
"""

import asyncio
import json
import logging
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.transport import get_connection, remove_connection

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


@app.websocket("/ws/signaling/{session_id}")
async def signaling_endpoint(websocket: WebSocket, session_id: str | None = None):
    """
    WebSocket endpoint for WebRTC signaling.

    Protocol:
    1. Client connects
    2. Client sends: {"type": "offer", "sdp": "..."}
    3. Server responds: {"type": "answer", "sdp": "..."}
    4. Both exchange: {"type": "ice-candidate", "candidate": {...}}
    5. WebRTC connection established
    6. WebSocket can close (or stay open for ICE trickling)
    """
    await websocket.accept()

    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    logger.info(f"New signaling connection: {session_id}")

    connection = get_connection(session_id)

    try:
        # Send session ID to client
        await websocket.send_json({
            "type": "session",
            "session_id": session_id,
        })

        while True:
            # Receive message from client
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "offer":
                # Handle SDP offer
                logger.info(f"Received offer from {session_id}")

                answer = await connection.handle_offer(
                    sdp=data["sdp"],
                    type_="offer",
                )

                await websocket.send_json({
                    "type": "answer",
                    "sdp": answer.sdp,
                })

                # Send any gathered ICE candidates
                if connection.pc:
                    @connection.pc.on("icecandidate")
                    async def on_ice_candidate(candidate):
                        if candidate:
                            await websocket.send_json({
                                "type": "ice-candidate",
                                "candidate": {
                                    "candidate": candidate.candidate,
                                    "sdpMid": candidate.sdpMid,
                                    "sdpMLineIndex": candidate.sdpMLineIndex,
                                },
                            })

            elif msg_type == "ice-candidate":
                # Handle ICE candidate from client
                candidate = data.get("candidate")
                if candidate:
                    await connection.add_ice_candidate(candidate)

            elif msg_type == "close":
                # Client requested close
                logger.info(f"Client requested close: {session_id}")
                break

    except WebSocketDisconnect:
        logger.info(f"Signaling disconnected: {session_id}")

    except Exception as e:
        logger.error(f"Signaling error for {session_id}: {e}")

    finally:
        # Note: Don't remove connection here, WebRTC might still be active
        # Connection cleanup happens when WebRTC disconnects
        pass



@app.on_event("shutdown")
async def shutdown():
    """Cleanup on server shutdown."""
    logger.info("Shutting down voice agent server...")
    # Close all active connections
    from src.transport import connections
    for session_id in list(connections.keys()):
        await remove_connection(session_id)
