"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  PipecatClient,
  PipecatClientOptions,
  RTVIEvent,
  TranscriptData
} from "@pipecat-ai/client-js";
import { WebSocketTransport } from "@pipecat-ai/websocket-transport";

export type ConnectionStatus = "idle" | "connecting" | "connected" | "error";

interface UseVoiceAgentOptions {
  /** HTTP server endpoint - defaults to env variable */
  endpoint?: string;
  /** Called when connection is established */
  onConnected?: () => void;
  /** Called when bot is ready */
  onBotReady?: (data: any) => void;
  /** Called when connection is closed */
  onDisconnected?: () => void;
  /** Called on error */
  onError?: (error: Error) => void;
  /** Called when user transcript is received */
  onUserTranscript?: (data: TranscriptData) => void;
  /** Called when bot transcript is received */
  onBotTranscript?: (data: any) => void;
}

interface UseVoiceAgentReturn {
  /** Current connection status */
  status: ConnectionStatus;
  /** Whether user's mic is muted */
  isMuted: boolean;
  /** Whether the bot is currently speaking */
  isBotSpeaking: boolean;
  /** Current user transcript */
  userText: string;
  /** Current bot transcript */
  botText: string;
  /** Connect to the voice agent */
  connect: () => Promise<void>;
  /** Disconnect from the voice agent */
  disconnect: () => void;
  /** Toggle microphone mute */
  toggleMute: () => void;
  /** Ref to attach to audio element for agent playback */
  audioRef: React.RefObject<HTMLAudioElement | null>;
}

export function useVoiceAgentWebSocket(
  options: UseVoiceAgentOptions = {}
): UseVoiceAgentReturn {
  const {
    endpoint = process.env.NEXT_PUBLIC_VOICE_AGENT_URL || "http://localhost:7860/connect",
    onConnected,
    onBotReady,
    onDisconnected,
    onError,
    onUserTranscript,
    onBotTranscript,
  } = options;

  const [status, setStatus] = useState<ConnectionStatus>("idle");
  const [isMuted, setIsMuted] = useState(false);
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const [userText, setUserText] = useState("");
  const [botText, setBotText] = useState("");

  const clientRef = useRef<PipecatClient | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  /**
   * Set up an audio track for playback
   * Handles both initial setup and track updates
   */
  const setupAudioTrack = useCallback(async (track: MediaStreamTrack) => {
    console.log("[VoiceAgent] Setting up audio track");
    if (audioRef.current) {
      if (
        audioRef.current.srcObject &&
        "getAudioTracks" in audioRef.current.srcObject
      ) {
        const oldTrack = audioRef.current.srcObject.getAudioTracks()[0];
        if (oldTrack?.id === track.id) return;
      }
      audioRef.current.srcObject = new MediaStream([track]);

      // Ensure audio element is ready to play
      try {
        audioRef.current.muted = false;
        audioRef.current.volume = 1.0;
        await audioRef.current.play();
        console.log("[VoiceAgent] Audio track playing");
      } catch (error) {
        console.error("[VoiceAgent] Failed to play audio track:", error);
      }

      setIsBotSpeaking(true);
    }
  }, []);

  /**
   * Check for available media tracks and set them up if present
   */
  const setupMediaTracks = useCallback(() => {
    if (!clientRef.current) return;
    const tracks = clientRef.current.tracks();
    if (tracks.bot?.audio) {
      setupAudioTrack(tracks.bot.audio);
    }
  }, [setupAudioTrack]);

  /**
   * Set up listeners for track events (start/stop)
   */
  const setupTrackListeners = useCallback(() => {
    if (!clientRef.current) return;

    // Listen for new tracks starting
    clientRef.current.on(RTVIEvent.TrackStarted, async (track, participant) => {
      console.log(`[VoiceAgent] Track started: ${track.kind} from ${participant?.name || "unknown"}, local: ${participant?.local}`);
      // Only handle non-local (bot) tracks
      if (!participant?.local && track.kind === "audio") {
        console.log("[VoiceAgent] Setting up bot audio track for playback");
        await setupAudioTrack(track);
      }
    });

    // Listen for tracks stopping
    clientRef.current.on(RTVIEvent.TrackStopped, (track, participant) => {
      console.log(`[VoiceAgent] Track stopped: ${track.kind} from ${participant?.name || "unknown"}`);
      if (track.kind === "audio") {
        setIsBotSpeaking(false);
      }
    });
  }, [setupAudioTrack]);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (clientRef.current) {
      try {
        clientRef.current.disconnect();
      } catch (e) {
        console.error("[VoiceAgent] Cleanup error:", e);
      }
      clientRef.current = null;
    }

    // Stop and cleanup audio tracks
    if (audioRef.current?.srcObject && "getAudioTracks" in audioRef.current.srcObject) {
      audioRef.current.srcObject.getAudioTracks().forEach((track) => track.stop());
      audioRef.current.srcObject = null;
    }

    setIsBotSpeaking(false);
    setIsMuted(false);
    setUserText("");
    setBotText("");
  }, []);

  // Connect to voice agent
  const connect = useCallback(async () => {
    if (status === "connecting" || status === "connected") {
      return;
    }

    try {
      const startTime = Date.now();
      setStatus("connecting");

      // Configure Pipecat client following reference implementation
      const clientConfig: PipecatClientOptions = {
        transport: new WebSocketTransport(),
        enableMic: true,
        enableCam: false,
        callbacks: {
          onConnected: () => {
            console.log("[VoiceAgent] Connected");
            setStatus("connected");
            onConnected?.();
          },
          onDisconnected: () => {
            console.log("[VoiceAgent] Disconnected");
            setStatus("idle");
            onDisconnected?.();
            cleanup();
          },
          onBotReady: async (data) => {
            console.log(`[VoiceAgent] Bot ready: ${JSON.stringify(data)}`);

            // Ensure audio element is ready for playback
            if (audioRef.current) {
              try {
                audioRef.current.muted = false;
                audioRef.current.volume = 1.0;
                console.log("[VoiceAgent] Audio element initialized for playback");
              } catch (error) {
                console.error("[VoiceAgent] Failed to initialize audio element:", error);
              }
            }

            setupMediaTracks();
            onBotReady?.(data);
          },
          onUserTranscript: (data) => {
            if (data.final) {
              console.log(`[VoiceAgent] User: ${data.text}`);
              setUserText(data.text);
              onUserTranscript?.(data);
            }
          },
          onBotTranscript: (data) => {
            console.log(`[VoiceAgent] Bot: ${data.text}`);
            setBotText(data.text);
            onBotTranscript?.(data);
          },
          onMessageError: (error) => {
            console.error("[VoiceAgent] Message error:", error);
          },
          onError: (error) => {
            console.error("[VoiceAgent] Error:", error);
            setStatus("error");
            onError?.(error instanceof Error ? error : new Error(String(error)));
          },
        },
      };

      // Create client
      const client = new PipecatClient(clientConfig);
      clientRef.current = client;

      // Set up track listeners
      setupTrackListeners();

      console.log("[VoiceAgent] Initializing devices...");
      await client.initDevices();

      console.log("[VoiceAgent] Connecting to bot at:", endpoint);
      await client.startBotAndConnect({
        endpoint: endpoint,
      });

      const timeTaken = Date.now() - startTime;
      console.log(`[VoiceAgent] Connection complete, time taken: ${timeTaken}ms`);
    } catch (err) {
      console.error("[VoiceAgent] Connection error:", err);
      setStatus("error");
      onError?.(err instanceof Error ? err : new Error(String(err)));
      cleanup();
    }
  }, [status, endpoint, onConnected, onBotReady, onDisconnected, onError, onUserTranscript, onBotTranscript, cleanup, setupMediaTracks, setupTrackListeners]);

  // Disconnect from voice agent
  const disconnect = useCallback(async () => {
    if (clientRef.current) {
      try {
        await clientRef.current.disconnect();
      } catch (error) {
        console.error("[VoiceAgent] Error disconnecting:", error);
      }
    }
    cleanup();
    setStatus("idle");
  }, [cleanup]);

  // Toggle microphone mute
  const toggleMute = useCallback(() => {
    if (clientRef.current) {
      try {
        if (isMuted) {
          clientRef.current.enableMic(true);
          setIsMuted(false);
        } else {
          clientRef.current.enableMic(false);
          setIsMuted(true);
        }
      } catch (e) {
        console.error("[VoiceAgent] Toggle mute error:", e);
      }
    }
  }, [isMuted]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return {
    status,
    isMuted,
    isBotSpeaking,
    userText,
    botText,
    connect,
    disconnect,
    toggleMute,
    audioRef,
  };
}
