"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/app/stores/auth-store";
import { refreshToken } from "@/app/api/auth";

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const setUser = useAuthStore((state) => state.setUser);
  const setLoading = useAuthStore((state) => state.setLoading);

  useEffect(() => {
    async function initAuth() {
      setLoading(true);
      try {
        const response = await refreshToken();
        setUser(response.user, response.tokens.access_token);
      } catch {
        // User is not authenticated - this is expected for new visitors
      } finally {
        setLoading(false);
      }
    }

    initAuth();
  }, [setUser, setLoading]);

  return <>{children}</>;
}
