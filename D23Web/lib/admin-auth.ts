/**
 * Admin Authentication Utilities
 */

export interface AdminUser {
  username: string;
  role: string;
}

/**
 * Get auth token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('admin_token');
}

/**
 * Get admin user from localStorage
 */
export function getAdminUser(): AdminUser | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('admin_user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Logout admin user
 */
export function logout(apiBase: string): void {
  const token = getAuthToken();

  // Call logout endpoint
  if (token) {
    fetch(`${apiBase}/admin/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }).catch(() => {
      // Ignore errors
    });
  }

  // Clear local storage
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_user');
  localStorage.removeItem('admin_expires_at');

  // Redirect to login
  window.location.href = '/admin/login';
}

/**
 * Make authenticated API request
 */
export async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('No auth token found');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized
  if (response.status === 401) {
    logout(process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:9002');
    throw new Error('Unauthorized');
  }

  return response;
}
