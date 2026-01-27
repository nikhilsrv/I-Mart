"""
WebRTC transport using aiortc for direct browser-to-server connections.
"""

import asyncio
import fractions
import logging
from typing import Callable

from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaPlayer, MediaRecorder
from aiortc.mediastreams import MediaStreamTrack
from av import AudioFrame

from src.config import settings

logger = logging.getLogger(__name__)


class AudioTrackProcessor:
    """Processes incoming audio from WebRTC and provides audio output."""

    def __init__(self):
        self.input_queue: asyncio.Queue[AudioFrame] = asyncio.Queue()
        self.output_queue: asyncio.Queue[AudioFrame] = asyncio.Queue()

    async def receive_frame(self) -> AudioFrame:
        """Get next audio frame from browser."""
        return await self.input_queue.get()

    async def send_frame(self, frame: AudioFrame):
        """Queue audio frame to send to browser."""
        await self.output_queue.put(frame)


class IncomingAudioTrack(MediaStreamTrack):
    """Track that receives audio from the browser."""

    kind = "audio"

    def __init__(self, track: MediaStreamTrack, processor: AudioTrackProcessor):
        super().__init__()
        self._track = track
        self._processor = processor

    async def recv(self) -> AudioFrame:
        frame = await self._track.recv()
        # Queue for processing
        await self._processor.input_queue.put(frame)
        return frame


class OutgoingAudioTrack(MediaStreamTrack):
    """Track that sends audio to the browser (TTS output)."""

    kind = "audio"

    def __init__(self, processor: AudioTrackProcessor):
        super().__init__()
        self._processor = processor
        self._timestamp = 0
        self._sample_rate = 16000

    async def recv(self) -> AudioFrame:
        try:
            # Get frame from TTS output queue
            frame = await asyncio.wait_for(
                self._processor.output_queue.get(),
                timeout=0.1,
            )
            return frame
        except asyncio.TimeoutError:
            # Return silence if no audio available
            frame = AudioFrame(format="s16", layout="mono", samples=160)
            frame.sample_rate = self._sample_rate
            frame.pts = self._timestamp
            frame.time_base = fractions.Fraction(1, self._sample_rate)
            self._timestamp += 160
            return frame


class WebRTCConnection:
    """
    Manages a single WebRTC peer connection.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pc: RTCPeerConnection | None = None
        self.processor = AudioTrackProcessor()
        self._closed = False

    def _get_ice_servers(self) -> list[RTCIceServer]:
        """Get ICE server configuration."""
        servers = [RTCIceServer(urls=settings.STUN_SERVERS)]

        if settings.TURN_SERVER:
            servers.append(
                RTCIceServer(
                    urls=[settings.TURN_SERVER],
                    username=settings.TURN_USERNAME,
                    credential=settings.TURN_PASSWORD,
                )
            )

        return servers

    async def create_peer_connection(self) -> RTCPeerConnection:
        """Create and configure the peer connection."""
        config = RTCConfiguration(iceServers=self._get_ice_servers())
        self.pc = RTCPeerConnection(configuration=config)

        # Add outgoing audio track (for TTS)
        outgoing_track = OutgoingAudioTrack(self.processor)
        self.pc.addTrack(outgoing_track)

        # Handle incoming tracks
        @self.pc.on("track")
        async def on_track(track: MediaStreamTrack):
            logger.info(f"Received {track.kind} track from browser")
            if track.kind == "audio":
                # Wrap incoming track
                incoming = IncomingAudioTrack(track, self.processor)
                # Track will be consumed by the pipeline

        # Handle connection state changes
        @self.pc.on("connectionstatechange")
        async def on_connection_state_change():
            logger.info(f"Connection state: {self.pc.connectionState}")
            if self.pc.connectionState == "failed":
                await self.close()

        @self.pc.on("iceconnectionstatechange")
        async def on_ice_connection_state_change():
            logger.info(f"ICE state: {self.pc.iceConnectionState}")

        return self.pc

    async def handle_offer(self, sdp: str, type_: str) -> RTCSessionDescription:
        """
        Handle SDP offer from browser and create answer.

        Args:
            sdp: SDP offer string
            type_: SDP type (should be "offer")

        Returns:
            SDP answer
        """
        if not self.pc:
            await self.create_peer_connection()

        offer = RTCSessionDescription(sdp=sdp, type=type_)
        await self.pc.setRemoteDescription(offer)

        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        return self.pc.localDescription

    async def add_ice_candidate(self, candidate: dict):
        """Add ICE candidate from browser."""
        if self.pc and candidate:
            await self.pc.addIceCandidate(candidate)

    async def close(self):
        """Close the peer connection."""
        if not self._closed and self.pc:
            self._closed = True
            await self.pc.close()
            logger.info(f"Closed connection for session {self.session_id}")


# Active connections
connections: dict[str, WebRTCConnection] = {}


def get_connection(session_id: str) -> WebRTCConnection:
    """Get or create a connection for a session."""
    if session_id not in connections:
        connections[session_id] = WebRTCConnection(session_id)
    return connections[session_id]


async def remove_connection(session_id: str):
    """Remove and close a connection."""
    if session_id in connections:
        await connections[session_id].close()
        del connections[session_id]
