"use client";

import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-8">Welcome to Ecommerce</h1>
      <button
        onClick={() => router.push("/auth/login")}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Login
      </button>
    </div>
  );
}
