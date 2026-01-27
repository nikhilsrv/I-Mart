"""
Pipecat pipeline for voice processing.
Integrates STT (Deepgram) -> LangGraph Agent -> TTS (Deepgram)
"""

import asyncio
from typing import AsyncGenerator

from pipecat.frames.frames import (
    EndFrame,
    LLMMessagesFrame,
    TextFrame,
    TranscriptionFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import LLMResponseAggregator
from pipecat.processors.aggregators.sentence import SentenceAggregator
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.transports.base_transport import BaseTransport
from pipecat.vad.silero import SileroVADAnalyzer

from src.config import settings
from src.graph import process_message


class LangGraphProcessor(FrameProcessor):
    """
    Custom Pipecat processor that routes transcribed text to LangGraph agent.
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
                response = await process_message(text, self.session_id)
                # Send response to TTS
                await self.push_frame(TextFrame(text=response))

        else:
            # Pass through other frames
            await self.push_frame(frame, direction)


def create_pipeline(transport: BaseTransport, session_id: str) -> PipelineTask:
    """
    Create the voice processing pipeline.

    Args:
        transport: WebRTC transport for audio I/O
        session_id: Unique session identifier

    Returns:
        PipelineTask ready to run
    """

    # STT: Deepgram speech-to-text
    stt = DeepgramSTTService(
        api_key=settings.DEEPGRAM_API_KEY,
        language="en",
        model="nova-2",
    )

    # TTS: Deepgram text-to-speech
    tts = DeepgramTTSService(
        api_key=settings.DEEPGRAM_API_KEY,
        voice="aura-asteria-en",  # Natural female voice
    )

    # VAD: Voice Activity Detection
    vad = SileroVADAnalyzer()

    # LangGraph processor
    agent_processor = LangGraphProcessor(session_id)

    # Sentence aggregator to get complete sentences
    sentence_aggregator = SentenceAggregator()

    # Build the pipeline
    pipeline = Pipeline(
        [
            transport.input(),      # Audio from browser
            stt,                    # Speech to text
            sentence_aggregator,    # Aggregate into sentences
            agent_processor,        # Process with LangGraph
            tts,                    # Text to speech
            transport.output(),     # Audio back to browser
        ]
    )

    # Create and return the task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,  # Allow user to interrupt
            enable_metrics=True,
        ),
    )

    return task


async def run_pipeline(transport: BaseTransport, session_id: str):
    """
    Run the pipeline for a session.

    Args:
        transport: WebRTC transport
        session_id: Unique session identifier
    """
    task = create_pipeline(transport, session_id)

    # Send initial greeting
    greeting = "Hello! Welcome to I-Mart. How can I help you shop today?"
    await task.queue_frame(TextFrame(text=greeting))

    # Run until disconnected
    await task.run()
