"use client";
import { AArrowDown } from "lucide-react"; // Importa o ícone desejado
import { useRouter } from "next/navigation"; // Importa o useRouter do Next.js
// components/Card.js
import React from "react";
import { Button } from "./ui/button";

const Card = ({
  title,
  description,
  icon,
  link,
}: {
  title: string;
  description: string;
  icon: string;
  link?: string; // Define o tipo da propriedade link
}) => {
  const router = useRouter(); // Inicializa o router

  return (
    <div className="w-[328px] h-[156px] rounded-[12px] shadow-[0px_6px_16px_rgba(0,0,0,0.12)] bg-[white] p-4">
        <div className="flex items-center mb-4">
          <div className="text-blue-500 mr-2">
            {icon} {/* Renderiza o ícone passado como prop */}
          </div>
          <h2 className="font-bold text-xl">{title}</h2>
        </div>

        <p className="text-gray-700 text-base mb-4"> {/* Adicionando margin-bottom de 16px aqui */}
          {description}
        </p>

        <div className="mt-4">
          <Button
            onClick={() => router.push(link || "")} // Redireciona para a URL especificada
            className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
          >
            Acessar
          </Button>
        </div>
      </div>
  );
};

export default Card;
