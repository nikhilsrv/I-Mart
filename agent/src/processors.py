"""
Custom Pipecat processors for I-Mart voice agent.
"""
import logging

from pipecat.frames.frames import TranscriptionFrame, TextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from src.graph import process_message

logger = logging.getLogger(__name__)


class LangGraphProcessor(FrameProcessor):
    """
    Routes transcribed text to LangGraph agent.
    Maintains compatibility with LangGraph's session-based memory.
    """

    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id
        self._current_sentence = ""

    async def process_frame(self, frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            # Accumulate transcription
            if frame.text:
                self._current_sentence += frame.text

        elif isinstance(frame, TextFrame):
            # Full sentence received, process with LangGraph
            text = frame.text.strip()
            if text:
                logger.info(f"[Session {self.session_id}] User: {text}")
                response = await process_message(text, self.session_id)
                logger.info(f"[Session {self.session_id}] Agent: {response}")
                # Send response to TTS
                await self.push_frame(TextFrame(text=response))

        else:
            # Pass through other frames
            await self.push_frame(frame, direction)
