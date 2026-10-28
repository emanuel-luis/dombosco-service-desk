// pages/auth/callback.tsx
"use client"; // Certifique-se de que este componente é um Client Component

import { useRouter, useSearchParams } from "next/navigation"; // Importação correta para App Router
import { Suspense, useEffect } from "react";

const GoogleCallback = () => {
  const router = useRouter();
  const searchParams = useSearchParams(); // Obtém os parâmetros de busca
  const code = searchParams.get("code");
  const access_token = searchParams.get("access_token");
  const id_token = searchParams.get("id_token");

  console.log(code, "code");
  console.log(access_token, "access_token");

  console.log(id_token, "id_token");
  useEffect(() => {
    const fetchToken = async () => {
      if (code) {
        console.log();
        try {
          const response = await fetch(
            "http://localhost:8000/api/v1/auth/google/",
            {
              method: "POST",
              body: JSON.stringify({ code }),
              headers: {
                "Content-Type": "application/json",
              },
            }
          );
          console.log("aqui", response);
          const jwtData = await response.json();
          if (jwtData.token) {
            router.push("/"); // Redireciona para a página inicial
          } else {
            console.error("No token received");
          }
        } catch (error) {
          console.error("Error fetching token:", error);
        }
      }
    };

    fetchToken();
  }, [code, router]);

  return <div>Loading...</div>; // Exibe uma mensagem enquanto aguarda
};

export default function CallbackPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <GoogleCallback />
    </Suspense>
  );
}
