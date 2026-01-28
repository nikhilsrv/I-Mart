"use client";

import { useState } from "react";

type ConnectionStatus = "connecting" | "connected" | "error";

export default function AgentWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("connecting");

  // Simulate connection after 2 seconds (replace with actual agent connection logic)
  const handleOpen = () => {
    setIsOpen(true);
    setConnectionStatus("connecting");

    // Simulate connection delay - replace with actual agent connection
    setTimeout(() => {
      setConnectionStatus("connected");
    }, 2000);
  };

  const handleClose = () => {
    setIsOpen(false);
    setConnectionStatus("connecting");
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
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
                      connectionStatus === "connected"
                        ? "bg-green-400"
                        : connectionStatus === "connecting"
                          ? "bg-yellow-400 animate-pulse"
                          : "bg-red-400"
                    }`}
                  />
                  <span className="text-white/80 text-xs">
                    {connectionStatus === "connected"
                      ? "Connected"
                      : connectionStatus === "connecting"
                        ? "Connecting..."
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
            {connectionStatus === "connecting" ? (
              <LoadingState />
            ) : connectionStatus === "connected" ? (
              <ConnectedState />
            ) : (
              <ErrorState onRetry={() => setConnectionStatus("connecting")} />
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-3 bg-white">
            <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5">
              <MicIcon
                className={`w-5 h-5 ${
                  connectionStatus === "connected"
                    ? "text-indigo-600"
                    : "text-gray-400"
                }`}
              />
              <span className="text-gray-500 text-sm flex-1">
                {connectionStatus === "connected"
                  ? "Listening..."
                  : "Waiting for connection..."}
              </span>
              {connectionStatus === "connected" && (
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
function ConnectedState() {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      {/* Animated speaking indicator */}
      <div className="relative">
        <div className="w-20 h-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full flex items-center justify-center">
          <AgentIcon className="w-10 h-10 text-white" />
        </div>
        {/* Pulse rings */}
        <div className="absolute inset-0 w-20 h-20 bg-indigo-600/20 rounded-full animate-ping" />
        <div
          className="absolute inset-0 w-20 h-20 bg-indigo-600/10 rounded-full animate-pulse"
          style={{ animationDelay: "0.5s" }}
        />
      </div>

      <div>
        <p className="text-gray-700 font-medium">Assistant is ready</p>
        <p className="text-gray-500 text-sm mt-1">
          How can I help you today?
        </p>
      </div>

      {/* Sound wave visualization */}
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
          Unable to connect to the assistant
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
