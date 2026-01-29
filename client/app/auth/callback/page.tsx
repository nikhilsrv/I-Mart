"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { googleLogin, googleSignup, AuthApiError } from "@/app/api/auth";
import { useAuthStore } from "@/app/stores/auth-store";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const setUser = useAuthStore((state) => state.setUser);

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
        const data =
          state === "login"
            ? await googleLogin(code)
            : await googleSignup(code);

        setUser(data.user, data.tokens.access_token);
        router.push("/");
      } catch (err) {
        if (err instanceof AuthApiError) {
          setError(err.message);
        } else {
          setError("Authentication failed");
        }
      }
    };

    handleCallback();
  }, [searchParams, router, setUser]);

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

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center min-h-screen">
          <div className="text-lg">Loading...</div>
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
