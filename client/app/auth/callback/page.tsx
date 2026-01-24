"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const errorParam = searchParams.get("error");

      if (errorParam) {
        setError("Authentication was cancelled or failed");
        return;
      }

      if (!code || !state) {
        setError("Missing authentication parameters");
        return;
      }

      if (state !== "login" && state !== "signup") {
        setError("Invalid state parameter");
        return;
      }

      try {
        const endpoint =
          state === "login"
            ? `${process.env.NEXT_PUBLIC_API_URL}/auth/google/login`
            : `${process.env.NEXT_PUBLIC_API_URL}/auth/google/signup`;

        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || "Authentication failed");
        }

        const data = await response.json();

        localStorage.setItem("access_token", data.tokens.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));

        router.push("/");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Authentication failed");
      }
    };

    handleCallback();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-red-500 text-lg mb-4">{error}</div>
        <a href="/auth/login" className="text-blue-600 hover:underline">
          Back to Login
        </a>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="text-lg">Completing authentication...</div>
    </div>
  );
}
