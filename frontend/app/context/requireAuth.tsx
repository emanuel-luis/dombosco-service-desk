"use client"

// app/context/RequireAuth.tsx

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';

const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const router = useRouter();

    useEffect(() => {
        // Verifica se o token existe no localStorage
        const token = localStorage.getItem('token');

        if (!token) {
            // Se não houver token, redireciona para a página de login
            router.push('/login');
        } 
    }, [router]);

    // Renderiza os filhos se o token estiver presente
    return <>{children}</>;
};

export default RequireAuth;