"use client"

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';

const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('token');

        if (!token) {
            router.push('/login');
        } 
    }, [router]);

    return <>{children}</>;
};

export default RequireAuth;