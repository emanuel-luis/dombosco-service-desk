"use client";

import { useRouter } from "next/navigation";
import type React from "react";
import { useContext, useState } from "react";
import { FaSignOutAlt } from "react-icons/fa";
import { AuthContext } from "../context/authContext";
import formsServices from "../services/ContactsService";
import { Header } from "./header";
import { UNOFFICIAL_NOTICE } from "./footer";
import { Button } from "./ui/button";

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const authContext = useContext(AuthContext);
  const router = useRouter();

  if (!authContext) {
    return <div>Loading...</div>;
  }

  const { login, loginWithGoogle } = authContext;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (email === "" || password === "") {
      setError("Por favor, preencha todos os campos.");
      return;
    }

    try {
      const token = await formsServices.getToken(email, password);
      login(token.access);
      router.push("/");
    } catch (error) {
      setError("Erro ao fazer login.");
      console.log(await formsServices.getToken(email, password));
      console.error("Login error:", error);
    }
  };

  return (
    <>
      <Header showMenuButton={false} />
      <div className="max-w-lg mx-auto p-8">
        <h2 className="text-2xl font-semibold text-center">Login</h2>
        {error && (
          <p role="alert" className="text-destructive">
            {error}
          </p>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-brand-text"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full border border-input rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-brand-text"
            >
              <div className="flex justify-between">
                <span>Senha</span>
                <span className="text-primary cursor-pointer">
                  Esqueceu sua Senha?
                </span>
              </div>
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full border border-input rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <button
            type="submit"
            className="w-full mt-4 flex items-center justify-center bg-primary text-primary-foreground p-2 rounded-md hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition"
          >
            <FaSignOutAlt color="#fff" size={20} className="mr-2" /> Entrar
          </button>
        </form>
        <div className="flex items-center justify-center mt-2">
          <Button
            variant="link"
            onClick={() => {
              router.push("/createAccount");
            }}
          >
            Criar Conta
          </Button>
        </div>
        <p className="mt-6 rounded-md border border-border bg-card p-3 text-center text-sm text-brand-text">
          {UNOFFICIAL_NOTICE}
        </p>
      </div>
    </>
  );
};

export default LoginForm;
