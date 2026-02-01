"use client";

import { useState } from "react";
import { useVoiceAgentWebSocket } from "@/app/hooks/useVoiceAgentWebSocket";

export default function AgentWidget() {
  const [isOpen, setIsOpen] = useState(false);

  const {
    status,
    isMuted,
    connect,
    disconnect,
    toggleMute,
    audioRef,
  } = useVoiceAgentWebSocket({
    endpoint: process.env.NEXT_PUBLIC_VOICE_AGENT_URL || "http://localhost:8765/connect",
    onConnected: () => {
      console.log("[AgentWidget] Connected to voice agent");
    },
    onDisconnected: () => {
      console.log("[AgentWidget] Disconnected from voice agent");
    },
    onError: (error) => {
      console.error("[AgentWidget] Error:", error);
    },
  });

  // Connect when widget opens, disconnect when it closes
  const handleOpen = async () => {
    setIsOpen(true);
    // Wait for next tick to ensure audio element is mounted
    await new Promise(resolve => setTimeout(resolve, 0));
    connect();
  };

  const handleClose = () => {
    disconnect();
    setIsOpen(false);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {/* Hidden audio element for agent voice playback - always present */}
      <audio
        ref={audioRef}
        autoPlay
        playsInline
        muted={false}
        className="hidden"
      />

      {/* Chat Window */}
      {isOpen && (
        <div className="w-80 sm:w-96 h-[450px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <AgentIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold text-sm">
                  I-Mart Assistant
                </h3>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      status === "connected"
                        ? "bg-green-400"
                        : status === "connecting"
                          ? "bg-yellow-400 animate-pulse"
                          : "bg-red-400"
                    }`}
                  />
                  <span className="text-white/80 text-xs">
                    {status === "connected"
                      ? "Connected"
                      : status === "connecting"
                        ? "Connecting..."
                        : status === "error"
                          ? "Connection Failed"
                          : "Disconnected"}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-white/80 hover:text-white hover:bg-white/10 rounded-lg p-1.5 transition-colors"
            >
              <CloseIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Content Area */}
          <div className="flex-1 flex flex-col items-center justify-center p-6 bg-gray-50">
            {status === "connecting" || status === "idle" ? (
              <LoadingState />
            ) : status === "connected" ? (
              <ConnectedState isMuted={isMuted} onToggleMute={toggleMute} />
            ) : (
              <ErrorState onRetry={connect} />
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-3 bg-white">
            <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5">
              <button
                onClick={toggleMute}
                disabled={status !== "connected"}
                className={`p-1 rounded-full transition-colors ${
                  status === "connected"
                    ? isMuted
                      ? "bg-red-100 text-red-600"
                      : "hover:bg-indigo-100"
                    : ""
                }`}
              >
                {isMuted ? (
                  <MicOffIcon
                    className={`w-5 h-5 ${
                      status === "connected" ? "text-red-600" : "text-gray-400"
                    }`}
                  />
                ) : (
                  <MicIcon
                    className={`w-5 h-5 ${
                      status === "connected"
                        ? "text-indigo-600"
                        : "text-gray-400"
                    }`}
                  />
                )}
              </button>
              <span className="text-gray-500 text-sm flex-1">
                {status === "connected"
                  ? isMuted
                    ? "Microphone muted"
                    : "Listening..."
                  : "Waiting for connection..."}
              </span>
              {status === "connected" && !isMuted && (
                <div className="flex gap-0.5">
                  <span className="w-1 h-4 bg-indigo-600 rounded-full animate-sound-wave-1" />
                  <span className="w-1 h-4 bg-indigo-600 rounded-full animate-sound-wave-2" />
                  <span className="w-1 h-4 bg-indigo-600 rounded-full animate-sound-wave-3" />
                  <span className="w-1 h-4 bg-indigo-600 rounded-full animate-sound-wave-4" />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={isOpen ? handleClose : handleOpen}
        className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-105 active:scale-95 ${
          isOpen
            ? "bg-gray-700 hover:bg-gray-800"
            : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
        }`}
      >
        {isOpen ? (
          <CloseIcon className="w-6 h-6 text-white" />
        ) : (
          <AgentIcon className="w-7 h-7 text-white" />
        )}
      </button>
    </div>
  );
}

// Loading State Component
function LoadingState() {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-indigo-200 rounded-full" />
        <div className="absolute inset-0 w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
      <div>
        <p className="text-gray-700 font-medium">Connecting to Assistant</p>
        <p className="text-gray-500 text-sm mt-1">
          Please wait while we establish connection...
        </p>
      </div>
    </div>
  );
}

// Connected State Component
interface ConnectedStateProps {
  isMuted: boolean;
  onToggleMute: () => void;
}

function ConnectedState({ isMuted, onToggleMute }: ConnectedStateProps) {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      {/* Animated speaking indicator */}
      <div className="relative">
        <button
          onClick={onToggleMute}
          className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
            isMuted
              ? "bg-gray-400"
              : "bg-gradient-to-r from-indigo-600 to-purple-600"
          }`}
        >
          {isMuted ? (
            <MicOffIcon className="w-10 h-10 text-white" />
          ) : (
            <AgentIcon className="w-10 h-10 text-white" />
          )}
        </button>
        {/* Pulse rings - only show when not muted */}
        {!isMuted && (
          <>
            <div className="absolute inset-0 w-20 h-20 bg-indigo-600/20 rounded-full animate-ping" />
            <div
              className="absolute inset-0 w-20 h-20 bg-indigo-600/10 rounded-full animate-pulse"
              style={{ animationDelay: "0.5s" }}
            />
          </>
        )}
      </div>

      <div>
        <p className="text-gray-700 font-medium">
          {isMuted ? "Microphone muted" : "Assistant is listening"}
        </p>
        <p className="text-gray-500 text-sm mt-1">
          {isMuted ? "Click to unmute and start speaking" : "How can I help you today?"}
        </p>
      </div>

      {/* Sound wave visualization - only show when not muted */}
      {!isMuted && (
        <div className="flex items-end gap-1 h-8 mt-2">
          {[...Array(12)].map((_, i) => (
            <span
              key={i}
              className="w-1.5 bg-gradient-to-t from-indigo-600 to-purple-600 rounded-full animate-sound-bar"
              style={{
                animationDelay: `${i * 0.1}s`,
                height: "8px",
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Error State Component
function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
        <ErrorIcon className="w-8 h-8 text-red-600" />
      </div>
      <div>
        <p className="text-gray-700 font-medium">Connection Failed</p>
        <p className="text-gray-500 text-sm mt-1">
          Unable to connect to the assistant. Please check your microphone permissions.
        </p>
      </div>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  );
}

// Icon Components
function AgentIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 8V4H8" />
      <rect x="8" y="8" width="8" height="8" rx="2" />
      <path d="M16 8h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2" />
      <path d="M8 8H6a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" />
      <path d="M12 16v4" />
      <path d="M10 20h4" />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function MicIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  );
}

function MicOffIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="2" y1="2" x2="22" y2="22" />
      <path d="M18.89 13.23A7.12 7.12 0 0 0 19 12v-2" />
      <path d="M5 10v2a7 7 0 0 0 12 5" />
      <path d="M15 9.34V5a3 3 0 0 0-5.68-1.33" />
      <path d="M9 9v3a3 3 0 0 0 5.12 2.12" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  );
}

function ErrorIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" x2="12" y1="8" y2="12" />
      <line x1="12" x2="12.01" y1="16" y2="16" />
    </svg>
  );
}
