"use client";

import { signIn } from "next-auth/react";
import type React from "react";
import { useContext, useState } from "react";
import { FaGoogle, FaSignOutAlt } from "react-icons/fa";
import { Header } from "./header";
import { AuthContext } from "../context/authContext";
import formsServices from "../services/ContactsService";
import { useRouter } from "next/navigation";

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
      <div className="max-w-lg mx-auto p-8 min-w-[500px]">
        <h2 className="text-2xl font-semibold text-center">Login</h2>
        {error && <p className="text-red-500">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring focus:ring-blue-500"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              <div className="flex justify-between">
                <span>Senha</span>
                <span className="text-blue-500 cursor-pointer">
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
              className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            className="w-full mt-4 flex items-center justify-center bg-[#5061FC] text-white p-2 rounded-md hover:bg-blue-700 transition"
          >
            <FaSignOutAlt color="#fff" size={20} className="mr-2" /> Entrar
          </button>
        </form>
        <button
          type="button"
          onClick={loginWithGoogle}
          className="w-full mt-4 bg-red-600 text-white p-2 rounded-md flex items-center justify-center hover:bg-red-700 transition"
        >
          <FaGoogle color="#fff" size={20} className="mr-2" /> Entrar com Google
        </button>
      </div>
    </>
  );
};

export default LoginForm;
