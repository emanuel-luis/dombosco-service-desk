"use client";
import React, {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { api } from "../lib/api";
import { clearToken, getToken, setToken } from "../lib/client";
import { GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI } from "../lib/config";
import { parseRole } from "../lib/roles";
import { Role, UserInfo } from "../lib/types";

export interface AuthContextType {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  loginWithGoogle: () => void;
  user: UserInfo | null;
  role: Role;
  // True until the first /auth/user/ answer (or the lack of a token) is known.
  userLoading: boolean;
}

const defaultAuthContextValue: AuthContextType = {
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
  loginWithGoogle: () => {},
  user: null,
  role: "visitor",
  userLoading: true,
};
export const AuthContext = createContext<AuthContextType>(
  defaultAuthContextValue
);

export const useAuth = () => useContext(AuthContext);

export const AuthProviderJWT: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [userLoading, setUserLoading] = useState<boolean>(true);

  const loadUser = useCallback(async () => {
    if (!getToken()) {
      setIsAuthenticated(false);
      setUser(null);
      setUserLoading(false);
      return;
    }
    setIsAuthenticated(true);
    setUserLoading(true);
    try {
      setUser(await api.getUser());
    } catch {
      // a 401 already sent the user to /login; other errors leave the user unknown
      setUser(null);
    } finally {
      setUserLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- loads the user on mount
    loadUser();
  }, [loadUser]);

  const login = (token: string) => {
    setToken(token);
    loadUser();
  };

  const logout = () => {
    clearToken();
    setIsAuthenticated(false);
    setUser(null);
  };

  const loginWithGoogle = () => {
    const params = new URLSearchParams({
      client_id: GOOGLE_CLIENT_ID,
      redirect_uri: GOOGLE_REDIRECT_URI,
      response_type: "code",
      scope: "openid profile email",
      access_type: "offline",
      prompt: "consent",
    });
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        login,
        logout,
        loginWithGoogle,
        user,
        role: parseRole(user?.role),
        userLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
