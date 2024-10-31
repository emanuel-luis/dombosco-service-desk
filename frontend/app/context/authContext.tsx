"use client"

import React, { createContext, useState, ReactNode, useEffect } from 'react';

interface AuthContextType {
    isAuthenticated: boolean;
    login: (token: string) => void;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProviderJWT: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
        }
    }, []);

    const login = (token: string) => {
        localStorage.setItem('token', token); // Armazena o token no localStorage
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.removeItem('token'); // Remove o token do localStorage
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};