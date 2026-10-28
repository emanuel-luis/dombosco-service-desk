"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useContext, useEffect, useState } from "react";
import { AuthContext } from "../../../context/authContext";
import { request } from "../../../lib/client";
import { toMessage } from "../../../lib/errors";

const GoogleCallback = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useContext(AuthContext);
  const code = searchParams.get("code");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!code) return;
    // Exchanges the Google code for the API's JWT.
    request<{ access?: string }>("POST", "/auth/google/", {
      auth: false,
      body: { code },
      messages: { 400: "Não foi possível entrar com o Google." },
    })
      .then((data) => {
        if (!data?.access) {
          setError("Não foi possível entrar com o Google.");
          return;
        }
        login(data.access);
        router.push("/");
      })
      .catch((e) => setError(toMessage(e)));
    // login is recreated on every render; the code is what triggers the exchange
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, router]);

  if (error) {
    return (
      <p role="alert" className="p-8 text-center text-destructive">
        {error}
      </p>
    );
  }
  return <div className="p-8 text-center">Entrando...</div>;
};

export default function CallbackPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center">Entrando...</div>}>
      <GoogleCallback />
    </Suspense>
  );
}
