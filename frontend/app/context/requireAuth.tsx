"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";

const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();

  useEffect(() => {
    // Função para obter o valor de um cookie pelo nome
    const getCookie = (name: string) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(";").shift();
    };

    // Verifica o token no localStorage
    const tokenFromLocalStorage = localStorage.getItem("token");
    // Verifica o token nos cookies
    const tokenFromCookies = getCookie("token");

    // Se não houver token em nenhum dos lugares, redireciona para a página de login
    if (!tokenFromLocalStorage && !tokenFromCookies) {
      router.push("/login");
    }
  }, [router]);

  return <>{children}</>;
};

export default RequireAuth;
