"use client"; 

import { useParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { Header } from "../../_components/header";
import formsServices from "../../services/ContactsService";
import { Button } from "@/app/_components/ui/button";
import { useRouter } from "next/navigation";
import Loader from "@/app/_components/loader";


const columns = [
  { head: "Aluno", accessor: "student_name" },
  { head: "Data de Nascimento", accessor: "student_birth_date" },
  { head: "Série", accessor: "student_grade_year" },
  { head: "Turma", accessor: "student_class_name" },
  { head: "Data da Solicitação", accessor: "created_at" },
  { head: "Status", accessor: "status" },
];

export default function Solicitações() {
  const router = useParams();
  const rota = useRouter()

  const [data, setData] = useState([]);
  const [parent, setParent] = useState(true)
  const [isLoading, setIsLoading] = useState(true)

  const { nome } = router
  const nomeFiltrado = decodeURIComponent(String(nome).split('%20').join(' ')); 
  console.log("Nome filtrado:", nomeFiltrado);

  const handleUserForm = () => {
    
  }


  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await formsServices.listFormsByUser();
        const aplication = await formsServices.listAplications();
        const filteredApplications = aplication.filter((item: any) => 
          Array.isArray(item.groups) && item.groups.length === 1 && item.groups[0] === 1
        );
        
        if (filteredApplications.length > 0) {
          setParent(false);
        };

        const responseFiltered = response.filter((ele : any) => ele.student_name == nomeFiltrado)
        setData(responseFiltered);
        setIsLoading(false)

        } catch (error) {
        console.log('ERROR:', error);
        setData([]);
      } finally {
        setIsLoading(false)
      }
    };

    fetchData();
}, []);
  

  return (
    <>
     {isLoading ? <Loader isLoading={isLoading}/> : 
      <>
        <Header />
        <div className="max-w-2xl px-5 pt-5 bg-white min-h-[480px] mt-[72px] mx-auto rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)]">
          <Button onClick={() => rota.back()}><img className="-rotate-90" src="/arrow.svg"/></Button>
          <h2 className="text-xl font-bold">Solicitações</h2>
          <br/>
          { data.map(element => (
            
            <>
              <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg ">
                {/* Informações do Aluno */}
                <header className="mb-6">
                  <h1 className="text-2xl font-bold text-gray-800">
                    {element?.student_name || 'Aluno não encontrado'}
                  </h1>
                </header>

                {/* Série e Turma */}
                <section aria-labelledby="student-info" className="mb-6">
                  <h2 id="student-info" className="sr-only">Informações do Aluno</h2>
                  <dl className="text-gray-600">
                    <div className="flex items-center mb-2">
                      <dt className="font-semibold w-24">Série:</dt>
                      <dd className="text-lg">{element?.student_grade_year}ª Série</dd>
                    </div>
                    <div className="flex items-center">
                      <dt className="font-semibold w-24">Turma:</dt>
                      <dd className="text-lg">{element?.student_class_name}</dd>
                    </div>
                  </dl>
                </section>

                {/* Descrição do Problema */}
                <section aria-labelledby="issue-description" className="bg-gray-100 p-4 rounded-lg mb-6">
                  <h2 id="issue-description" className="text-lg font-semibold text-gray-800 mb-2">
                    Descrição do Problema
                  </h2>
                  <p className="text-gray-700">
                    {element?.issue_description || 'Nenhuma descrição disponível.'}
                  </p>
                </section>

                {/* Resposta do Colaborador */}
                {!parent 
                ? 
                <section aria-labelledby="collaborator-response" className="bg-blue-50 p-4 rounded-lg">
                  <h2 id="collaborator-response" className="text-lg font-semibold text-blue-800 mb-2">
                    Resposta do Colaborador
                  </h2>
                  <textarea
                    className="w-full h-32 p-3 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-400"
                    placeholder="Escreva sua resposta aqui..."
                  ></textarea>
                  <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" onClick={handleUserForm}>
                    Enviar Resposta
                  </button>

                  <h2 id="collaborator-response" className="text-lg font-semibold text-blue-800 mb-2">
                    O que fazer
                  </h2>
                  <textarea
                    className="w-full h-32 p-3 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-400"
                    placeholder="Escreva sua resposta aqui..."
                  ></textarea>
                  <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" onClick={handleUserForm}>
                    Enviar Resposta
                  </button>


                  <h2 id="collaborator-response" className="text-lg font-semibold text-blue-800 mb-2">
                    Medidas a tomar
                  </h2>
                  <textarea
                    className="w-full h-32 p-3 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-400"
                    placeholder="Escreva sua resposta aqui..."
                  ></textarea>
                  <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" onClick={handleUserForm}>
                    Enviar Resposta
                  </button>
                </section> 

                
                : 
                null }
              </div>
            </>
          )) 
          
          }
          
        </div>
        </>
     }
    </>
  );
}
