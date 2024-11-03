// pages/protected.tsx
"use client";
import { signIn, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const ProtectedPage: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "loading") {
      // Se a sessão está carregando, não faz nada
      return;
    }

    if (!session) {
      // Se não houver sessão, redireciona para a página de login
      router.push("/login");
    } else {
      router.push("/");
    }
  }, [session, status, router]);

  if (status === "loading") {
    return <p>Loading...</p>; // Exibir uma mensagem de carregamento enquanto verifica a sessão
  }
};

export default ProtectedPage;
