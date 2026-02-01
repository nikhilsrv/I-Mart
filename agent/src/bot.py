"""
Bot pipeline creation with RTVI protocol.
Integrates STT (Deepgram) -> LangGraph Agent -> TTS (Deepgram) with RTVI events.

This implementation follows the Pipecat reference architecture from websocket/server/bot_fast_api.py
"""
import logging

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.sentence import SentenceAggregator
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

from src.config import settings
from src.processors import LangGraphProcessor

logger = logging.getLogger(__name__)


async def run_bot(websocket_client):
    """
    Run the I-Mart voice agent bot.

    This function follows the Pipecat reference implementation pattern:
    - Accepts the raw websocket client from FastAPI
    - Creates FastAPIWebsocketTransport internally
    - Sets up the pipeline with STT, Agent, and TTS
    - Runs the pipeline with RTVI event handling

    Pipeline Flow:
    1. Audio from client → Deepgram STT
    2. STT → SentenceAggregator (complete sentences)
    3. Sentences → RTVI processor (event handling)
    4. RTVI → LangGraphProcessor (I-Mart agent with tools)
    5. Agent response → Deepgram TTS
    6. TTS → Audio back to client

    Args:
        websocket_client: FastAPI WebSocket connection
    """
    # Generate session ID from websocket client
    session_id = str(id(websocket_client))
    logger.info(f"Starting bot for session {session_id}")

    # Create transport with Pipecat protocol support
    ws_transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=ProtobufFrameSerializer(),
        ),
    )

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
        sample_rate=24000,
    )

    # LangGraph processor with session-based memory
    agent_processor = LangGraphProcessor(session_id)

    # Sentence aggregator for complete sentences
    sentence_aggregator = SentenceAggregator()

    # RTVI processor for client events
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Build pipeline
    pipeline = Pipeline([
        ws_transport.input(),      # Audio from WebSocket
        stt,                       # Speech to text
        sentence_aggregator,       # Aggregate into sentences
        rtvi,                      # RTVI event handling
        agent_processor,           # Process with LangGraph agent
        tts,                       # Text to speech
        ws_transport.output(),     # Audio back to WebSocket
    ])

    # Create task with RTVI observer
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,  # Allow user to interrupt
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    # Event handlers
    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        """Client ready - send bot ready and start conversation."""
        logger.info(f"[Session {session_id}] Pipecat client ready")
        await rtvi.set_bot_ready()
        # Send welcome message directly to TTS (bypass agent processor)
        welcome_message = "Hello! Welcome to I-Mart. How can I help you today?"
        await tts.say(welcome_message)
        logger.info(f"[Session {session_id}] Sent welcome message")

    @ws_transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        """WebSocket connected."""
        logger.info(f"[Session {session_id}] Pipecat client connected")

    @ws_transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        """WebSocket disconnected - cancel task."""
        logger.info(f"[Session {session_id}] Pipecat client disconnected")
        await task.cancel()

    # Run the pipeline
    runner = PipelineRunner(handle_sigint=False)

    try:
        await runner.run(task)
    except Exception as e:
        logger.error(f"Bot error for session {session_id}: {e}", exc_info=True)
    finally:
        logger.info(f"Bot ended for session {session_id}")
