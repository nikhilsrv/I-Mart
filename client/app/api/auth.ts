const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access_token: string;
    token_type: string;
  };
}

export interface ApiError {
  detail: string;
}

class AuthApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "AuthApiError";
  }
}

export async function googleLogin(code: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/google/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new AuthApiError(error.detail || "Login failed", response.status);
  }

  return response.json();
}

export async function googleSignup(code: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/google/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new AuthApiError(error.detail || "Signup failed", response.status);
  }

  return response.json();
}

export async function refreshToken(): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new AuthApiError(
      error.detail || "Token refresh failed",
      response.status
    );
  }

  return response.json();
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export { AuthApiError };
