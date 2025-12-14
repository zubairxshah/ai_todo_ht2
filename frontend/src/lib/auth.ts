"use client";

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

export const { signIn, signUp, signOut, useSession, getSession } = authClient;

// Helper to get JWT token from Better Auth
export async function getJwtToken(): Promise<string | null> {
  try {
    const response = await authClient.getSession({
      fetchOptions: {
        onSuccess: (ctx) => {
          // JWT is returned in the set-auth-jwt header
          const jwt = ctx.response.headers.get("set-auth-jwt");
          if (jwt) {
            // Store in sessionStorage for use in API calls
            sessionStorage.setItem("auth-jwt", jwt);
          }
        },
      },
    });

    // Return from sessionStorage if available
    return sessionStorage.getItem("auth-jwt");
  } catch {
    return null;
  }
}
