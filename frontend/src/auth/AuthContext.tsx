import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import * as api from "../api/client";
import { ApiError, type LoginBody, type User } from "../api/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (body: LoginBody) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // On app start, ask the server whether a session already exists.
  useEffect(() => {
    let cancelled = false;
    const checkSession = async () => {
      try {
        const current = await api.me();
        if (!cancelled) setUser(current);
      } catch (error) {
        // 401 simply means "not logged in". Anything else: stay logged out.
        if (!(error instanceof ApiError) && !cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void checkSession();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (body: LoginBody) => {
    await api.login(body);
    const current = await api.me();
    setUser(current);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
