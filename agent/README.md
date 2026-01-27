# I-Mart Voice Agent

Voice-enabled shopping assistant using Pipecat and LangGraph.

## Architecture

```
Browser (WebRTC) ←→ Signaling Server ←→ Pipecat Pipeline
                                            │
                                    ┌───────┴───────┐
                                    │               │
                              Deepgram STT    LangGraph Agent
                                    │               │
                              Deepgram TTS    I-Mart API
```

## Setup

1. Create virtual environment:
```bash
cd agent
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -e .
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```bash
python -m src.main
```

## API Keys Required

- **OpenAI**: Get from https://platform.openai.com/api-keys
- **Deepgram**: Get from https://console.deepgram.com/

## Endpoints

- `GET /health` - Health check
- `WS /ws/signaling/{session_id}` - WebRTC signaling

## Project Structure

```
agent/
├── src/
│   ├── config.py      # Settings and environment variables
│   ├── tools.py       # LangGraph tools (search, cart, etc.)
│   ├── prompts.py     # System prompts for the agent
│   ├── graph.py       # LangGraph agent setup
│   ├── pipeline.py    # Pipecat STT → Agent → TTS pipeline
│   ├── transport.py   # WebRTC connection handling
│   ├── server.py      # FastAPI signaling server
│   └── main.py        # Entry point
├── .env.example
├── pyproject.toml
└── README.md
```
