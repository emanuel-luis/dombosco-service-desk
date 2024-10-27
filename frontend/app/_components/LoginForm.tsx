"use client";

import { signIn } from "next-auth/react";
import type React from "react";
import { useState } from "react";
import { FaGoogle, FaSignOutAlt } from "react-icons/fa";
import { Header } from "./header";

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Aqui você pode adicionar sua lógica de autenticação com email e senha

    if (email === "" || password === "") {
      setError("Por favor, preencha todos os campos.");
      return;
    }

    console.log("Email:", email);
    console.log("Senha:", password);
  };

  return (
    <>
    <Header/>
    <div className="max-w-lg mx-auto p-8 min-w-[500px]">
      <h2 className="text-2xl font-semibold text-center">Login</h2>
      {error && <p className="text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700"
          >
            Email Aluno
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
            <span className="text-blue-500 cursor-pointer">Esqueceu sua Senha?</span>
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
        onClick={() => signIn("google", { callbackUrl: "/" })}
        className="w-full mt-4 bg-red-600 text-white p-2 rounded-md flex items-center justify-center hover:bg-red-700 transition"
      >
        <FaGoogle color="#fff" size={20} className="mr-2" /> Entrar com Google
      </button>
      {/* <p className="text-center mt-8 text-[#98A2B3]">
        Acesso para colaboradores. <a className=" text-[#1570EF] cursor-pointer ">Clique Aqui</a>
      </p> */}
    </div>
    </>
  );
};

export default LoginForm;
