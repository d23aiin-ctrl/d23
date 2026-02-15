"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:9002";

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("admin_token");
      const expiresAt = localStorage.getItem("admin_expires_at");

      if (!token) {
        router.push("/admin/login");
        return;
      }

      // Check if token expired
      if (expiresAt) {
        const expiry = new Date(expiresAt);
        if (expiry < new Date()) {
          localStorage.removeItem("admin_token");
          localStorage.removeItem("admin_user");
          localStorage.removeItem("admin_expires_at");
          router.push("/admin/login");
          return;
        }
      }

      // Verify token with server
      try {
        const response = await fetch(`${apiBase}/admin/verify`, {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Invalid token");
        }

        setIsAuthenticated(true);
      } catch (error) {
        // Token invalid, clear and redirect
        localStorage.removeItem("admin_token");
        localStorage.removeItem("admin_user");
        localStorage.removeItem("admin_expires_at");
        router.push("/admin/login");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, apiBase]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-emerald-500" />
          <p className="text-sm text-[var(--muted-foreground)]">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Router will redirect
  }

  return <>{children}</>;
}
