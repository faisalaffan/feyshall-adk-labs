---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Bidirectional Audio (Gemini Live API)

## Concept

Gemini's Live API enables real-time audio conversations — the agent listens while you speak and responds with voice. This is the technology behind Google's conversational AI demos.

## Architecture

```
Browser (Web Audio API)
    │  Mic input (PCM audio chunks)
    ▼
WebSocket ──► Gemini Live API
    │             │
    │         Agent loop
    │             │
    ▼             ▼
Speaker ◄── Audio output (PCM)
```

## Code (Server)

```python
import asyncio
import websockets
from google.adk.agents import Agent
from google.adk.audio import LiveAudioSession

agent = Agent(
    name="voice-assistant",
    model="gemini-2.5-flash",
    instruction="You are a voice assistant. Keep responses brief and conversational.",
)

async def handle_audio_websocket(websocket):
    session = await LiveAudioSession.create(agent=agent)

    async def receive_audio():
        """Receive audio chunks from browser, send to Gemini."""
        async for message in websocket:
            if isinstance(message, bytes):
                await session.send_audio(message)

    async def send_audio():
        """Receive audio responses from Gemini, send to browser."""
        async for audio_chunk in session.receive_audio():
            await websocket.send(audio_chunk)

    await asyncio.gather(receive_audio(), send_audio())

asyncio.run(websockets.serve(handle_audio_websocket, "0.0.0.0", 8765))
```

## Client (Browser)

```javascript
const ws = new WebSocket("ws://localhost:8765");
const audioContext = new AudioContext();
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const source = audioContext.createMediaStreamSource(stream);
const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
  const pcm = e.inputBuffer.getChannelData(0);
  ws.send(new Float32Array(pcm).buffer);
};

ws.onmessage = async (event) => {
  const audioBuffer = await audioContext.decodeAudioData(event.data);
  const player = audioContext.createBufferSource();
  player.buffer = audioBuffer;
  player.connect(audioContext.destination);
  player.start();
};
```

## Pitfalls

- **Live API is Gemini-only**: Claude, GPT, and Ollama don't support bidirectional audio. This is a vendor lock-in feature.
- **Audio format**: Live API expects PCM 16kHz mono. Resampling on the client adds CPU cost (mobile users notice).
- **Latency targets**: >500ms round-trip feels unnatural. Use a model close to your users' region.
- **Reconnection is complex**: Dropped WebSocket mid-conversation requires full reconnection + session restore.
