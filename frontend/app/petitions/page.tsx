"use client"; 

import React, { useEffect, useState } from "react";
import { Header } from "../_components/header";
import TableGrid from "../_components/tableGrid";
import { Button } from "../_components/ui/button";
import { useRouter } from "next/navigation";
import formsServices from "../services/ContactsService";
import Loader from "@/app/_components/loader";

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

  const [data, setData] = useState([]);
  const [application, setApplication] = useState([]);
  const [email, setEmail] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [userStaff, setUserStaff] = useState(false)


  useEffect(() => {
    const applications = async () => {
      const data = await formsServices.listAplications()
      setApplication(data)

      const containsGroup2 = data.some((app: any) => app.groups && app.groups.length === 1 && app.groups[0] === 2);

      if (containsGroup2) {
        setUserStaff(true);
      }
    }

    applications()
  }, [])

    useEffect(() => {
      const fetchData = async () => {
        try {
          const response = await formsServices.listFormsByUser();
          const { email } = await formsServices.listUser()

          setEmail(email)
          setData(response);
          setIsLoading(false)

        } catch (error) {
          setData([]);
        } finally {
          setIsLoading(false)
        }
      };

      fetchData();
  }, []);
    
  const currentData = Array.isArray(data) && data.length > 0 ? data : []; 

  return (
    <>
     {isLoading ? <Loader isLoading={isLoading}/> : 
     <>
     <Header />
     <div className="flex flex-col px-5 pt-5 bg-[white] min-h-[550px] mt-[72px] mx-[115px] rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)] ">
        <Button
          variant="link"
          className="self-start"
          onClick={() => router.back()}
        >
          <img className="-rotate-90" src="/arrow.svg" />
        </Button>
        <h2 className="text-xl font-bold">Solicitações</h2>
        {application?.map(element => {
          if (String(element?.description).toLowerCase() == "ATENDIMENTOS".toLowerCase() && !userStaff) {
            return (
            <button onClick={() => router.push('/persons-responsible')} type="button" className="self-end text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
              Criar Solicitação
            </button>
            )}
        })}
        <TableGrid columns={columns} data={currentData} email={email}/>

      </div>
      </>
     }
    </>
  );
}
