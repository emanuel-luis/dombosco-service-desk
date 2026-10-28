"use client";

import React, { useEffect, useState } from "react";
import { Header } from "../_components/header";
import TableGrid from "../_components/tableGrid";
import { Button } from "../_components/ui/button";
import { useRouter } from "next/navigation";
import { BackArrow } from "@/app/_components/BackArrow";
import Loader from "@/app/_components/loader";
import { useAuth } from "../context/authContext";
import { api } from "../lib/api";
import { toMessage } from "../lib/errors";
import { canCreateRequest } from "../lib/roles";
import { ParentForm } from "../lib/types";

const columns = [
  { head: 'ID', accessor: "id"},
  { head: "Aluno", accessor: "student_name" },
  { head: "Data de Nascimento", accessor: "student_birth_date" },
  { head: "Série", accessor: "student_grade_year" },
  { head: "Turma", accessor: "student_class_name" },
  { head: "Data da Solicitação", accessor: "created_at" },
  { head: "Status", accessor: "status" },
];

export default function Solicitações() {
  const router = useRouter();
  const { role, user, userLoading } = useAuth();

  const [data, setData] = useState<ParentForm[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // The API already limits the list to what this user may see.
    api
      .listForms()
      .then(setData)
      .catch((e) => setError(toMessage(e)))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <>
     {isLoading || userLoading ? <Loader isLoading /> :
     <>
     <Header />
     <div className="flex flex-col px-5 pt-5 bg-card min-h-[550px] mt-[72px] mx-[115px] rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)] ">
        <Button
          variant="link"
          className="self-start"
          onClick={() => router.back()}
        >
          <BackArrow />
        </Button>
        <h2 className="text-xl font-bold">Solicitações</h2>
        {error && (
          <p role="alert" className="text-destructive text-sm my-2">
            {error}
          </p>
        )}
        {canCreateRequest(role) && (
          <button onClick={() => router.push('/persons-responsible')} type="button" className="self-end text-white bg-secondary hover:bg-brand-magenta-dark focus:ring-4 focus:ring-ring font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none">
            Criar Solicitação
          </button>
        )}
        <TableGrid columns={columns} data={data} role={role} user={user}/>

      </div>
      </>
     }
    </>
  );
}
