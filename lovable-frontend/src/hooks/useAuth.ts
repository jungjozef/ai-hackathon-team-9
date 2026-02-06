import { useCallback, useEffect, useMemo, useState } from "react";
import { authStorage, fetchAuthUrl, fetchMe, ApiUser } from "@/lib/api";

const TOKEN_PARAM = "token";

function parseTokenFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search);
  const token = params.get(TOKEN_PARAM);
  if (!token) {
    return null;
  }
  params.delete(TOKEN_PARAM);
  const newQuery = params.toString();
  const newUrl = newQuery ? `${window.location.pathname}?${newQuery}` : window.location.pathname;
  window.history.replaceState({}, "", newUrl);
  return token;
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(() => authStorage.getToken());
  const [user, setUser] = useState<ApiUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const tokenFromUrl = parseTokenFromUrl();
    if (tokenFromUrl) {
      authStorage.setToken(tokenFromUrl);
      setToken(tokenFromUrl);
    }
  }, []);

  useEffect(() => {
    const loadMe = async () => {
      if (!token) {
        setUser(null);
        setError(null);
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const me = await fetchMe();
        setUser(me);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to authenticate.";
        setError(message);
        authStorage.clearToken();
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadMe();
  }, [token]);

  const login = useCallback(async () => {
    const url = await fetchAuthUrl();
    window.location.href = url;
  }, []);

  const logout = useCallback(() => {
    authStorage.clearToken();
    setToken(null);
    setUser(null);
  }, []);

  const isAuthenticated = useMemo(() => Boolean(token && user), [token, user]);

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
  };
}
