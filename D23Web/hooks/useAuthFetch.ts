import { useCallback, useMemo } from 'react';
import { getAuthToken, logout } from '@/lib/admin-auth';

export function useAuthFetch(apiBase: string) {
  const token = useMemo(() => getAuthToken(), []);

  const authFetch = useCallback(
    async (url: string, options: RequestInit = {}) => {
      const headers = new Headers(options.headers);

      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Auto-logout on 401
      if (response.status === 401) {
        logout(apiBase);
        throw new Error('Unauthorized');
      }

      return response;
    },
    [token, apiBase]
  );

  return authFetch;
}
