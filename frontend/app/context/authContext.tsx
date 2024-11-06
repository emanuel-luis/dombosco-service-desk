"use client";
import { useParams } from "next/navigation";
import React, { createContext, useState, ReactNode, useEffect } from "react";
import formsServices from "../services/ContactsService";

export interface AuthContextType {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  loginWithGoogle: () => void; // Novo método para login com Google
  user: any
}

const defaultAuthContextValue: AuthContextType = {
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
  loginWithGoogle: () => {},
  user: {}
};
export const AuthContext = createContext<AuthContextType>(
  defaultAuthContextValue
);

export const AuthProviderJWT: React.FC<{ children: ReactNode }> = ({
  children, 
}) => {
  const router = useParams();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("token");

      if (token) {
        try {
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Erro ao buscar dados do usuário:', error);
        }
      } else {
        setIsAuthenticated(false);
      }
    };

    fetchUserData(); // Chama a função assíncrona
  }, []); 

  const login = (token: string) => {
    localStorage.setItem("token", token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
  };

  const loginWithGoogle = async () => {
    const clientId =
      "257773922983-1l654u5ao8b3a8kfobsktqd22ro2g6l3.apps.googleusercontent.com"; // Certifique-se de definir esta variável no .env.local
    const redirectUri = `http://localhost:3000/api/auth/callback`;

    const authUrl =
      `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}&` +
      `redirect_uri=${redirectUri}&` +
      `response_type=code&` +
      `scope=openid%20profile%20email&` +
      "access_type=offline" +
      "&prompt=consent";

    window.location.href = authUrl; // Redireciona o usuário para o Google
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, login, logout, loginWithGoogle }}
    >
      {children}
    </AuthContext.Provider>
  );
};
