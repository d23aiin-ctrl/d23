"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import authFetch from "@/lib/auth_fetch";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

type Status = "pending" | "success" | "error";

function GmailCallbackContent() {
  const params = useSearchParams();
  const router = useRouter();
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api"; // Use Next.js proxy to avoid CORS
  const [status, setStatus] = useState<Status>("pending");
  const [message, setMessage] = useState("Completing Gmail connection...");

  useEffect(() => {
    const code = params.get("code");
    if (!code) {
      setStatus("error");
      setMessage("Missing authorization code. Try connecting Gmail again.");
      return;
    }
    const state = params.get("state");

    // Validate CSRF state token
    const storedState = sessionStorage.getItem("oauth_state");
    if (!state || state !== storedState) {
      setStatus("error");
      setMessage("Invalid OAuth state. This may be a CSRF attack. Please try connecting Gmail again from Settings.");
      sessionStorage.removeItem("oauth_state");
      return;
    }
    sessionStorage.removeItem("oauth_state");

    const completeConnection = async () => {
      try {
        const response = await authFetch(`${apiBase}/auth/providers/gmail/exchange`, {
          method: "POST",
          body: JSON.stringify({ code, state }),
        });

        if (!response.ok) {
          let detail = "Failed to complete Gmail connection.";
          try {
            const error = await response.json();
            detail = error.detail || detail;
          } catch {
            // Ignore JSON parsing errors
          }
          throw new Error(detail);
        }

        setStatus("success");
        setMessage("Gmail connected! Redirecting...");
        setTimeout(() => router.replace("/settings"), 1200);
      } catch (error) {
        setStatus("error");
        setMessage((error as Error).message || "Failed to connect Gmail. Please try again.");
      }
    };

    completeConnection();
  }, [apiBase, params, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <div className="max-w-md w-full bg-white border border-neutral-200 rounded-xl p-8 shadow-sm">
        <div className="flex flex-col items-center gap-4">
          {status === "pending" && <Loader2 className="h-12 w-12 animate-spin text-violet-500" />}
          {status === "success" && <CheckCircle2 className="h-12 w-12 text-green-500" />}
          {status === "error" && <XCircle className="h-12 w-12 text-red-500" />}

          <h2 className="text-xl font-semibold text-neutral-900">Gmail Authorization</h2>
          <p className="text-sm text-neutral-500 text-center">{message}</p>

          {status === "error" && (
            <button
              onClick={() => router.push("/settings")}
              className="mt-4 px-6 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-colors"
            >
              Back to Settings
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function GmailCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-white px-4">
          <div className="max-w-md w-full bg-white border border-neutral-200 rounded-xl p-8 shadow-sm">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-12 w-12 animate-spin text-violet-500" />
              <h2 className="text-xl font-semibold text-neutral-900">Gmail Authorization</h2>
              <p className="text-sm text-neutral-500 text-center">Loading...</p>
            </div>
          </div>
        </div>
      }
    >
      <GmailCallbackContent />
    </Suspense>
  );
}
