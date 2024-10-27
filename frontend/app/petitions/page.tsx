"use client"; // Indica que este é um componente de cliente
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { Header } from "../_components/header";
import TableGrid from "../_components/tableGrid";
import { Button } from "../_components/ui/button";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../_components/ui/tabs";

import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
} from "../pagination";

const columns = [
  { head: "Aluno", accessor: "aluno" },
  { head: "Série", accessor: "serie" },
  { head: "Telefone", accessor: "telefone" },
  { head: "Email", accessor: "email" },
  { head: "Data", accessor: "data" },
  { head: "Status", accessor: "status" },
];

const data = [
  {
    aluno: "Tarcisio Silva",
    serie: "5º Ano",
    telefone: "(11) 91234-5678",
    email: "tarcisio.silva@example.com",
    data: "2024-10-25",
    status: "Ativo",
  },
  {
    aluno: "Maria Oliveira",
    serie: "6º Ano",
    telefone: "(11) 98765-4321",
    email: "maria.oliveira@example.com",
    data: "2024-10-24",
    status: "Inativo",
  },
  {
    aluno: "João Santos",
    serie: "7º Ano",
    telefone: "(11) 99876-5432",
    email: "joao.santos@example.com",
    data: "2024-10-23",
    status: "Ativo",
  },
  {
    aluno: "Ana Paula",
    serie: "5º Ano",
    telefone: "(11) 92345-6789",
    email: "ana.paula@example.com",
    data: "2024-10-22",
    status: "Ativo",
  },
  {
    aluno: "Carlos Alberto",
    serie: "8º Ano",
    telefone: "(11) 93456-7890",
    email: "carlos.alberto@example.com",
    data: "2024-10-21",
    status: "Aguardando Documentação",
  },
  {
    aluno: "Fernanda Lima",
    serie: "6º Ano",
    telefone: "(11) 94567-8901",
    email: "fernanda.lima@example.com",
    data: "2024-10-20",
    status: "Ativo",
  },
];

export default function Solicitações() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 10;

  
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  return (
    <>
      <Header />
      <div className="px-5 pt-5 bg-[white] mh-[480px] mt-[72px] mr-[115px] ml-[115px] rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)]">
        <Tabs defaultValue="account" className="w-[400px]">
          <TabsList>
            <TabsTrigger value="account">Account</TabsTrigger>
            <TabsTrigger value="password">Password</TabsTrigger>
          </TabsList>
          <TabsContent value="account">
            Make changes to your account here.
          </TabsContent>
          <TabsContent value="password"></TabsContent>
        </Tabs>

        <h2 className="text-xl font-bold">Solicitações</h2>
        <TableGrid columns={columns} data={data} />

      <div>
        <Pagination>
          <PaginationContent>
            <PaginationPrevious disabled={currentPage === 1} onClick={() => handlePageChange(currentPage - 1)}>
              <span>Previous</span>
            </PaginationPrevious>

            {[...Array(totalPages)].map((_, index) => {
              const pageNumber = index + 1;
              return (
                <PaginationItem key={pageNumber}>
                  <PaginationLink
                    isActive={currentPage === pageNumber}
                    onClick={() => handlePageChange(pageNumber)}
                  >
                    {pageNumber}
                  </PaginationLink>
                </PaginationItem>
              );
            })}

            <PaginationEllipsis />

            <PaginationNext disabled={currentPage === totalPages} onClick={() => handlePageChange(currentPage + 1)}>
            <span>Next</span>
          </PaginationNext>
        </PaginationContent>
      </Pagination>
    </div>

        <Button
          variant="link"
          onClick={() => router.back()} // Navega para a página anterior
          className="mt-4"
        >
          Voltar
        </Button>
      </div>
    </>
  );
}
