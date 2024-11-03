"use client"; 

import React, { useEffect, useState } from "react";
import { Header } from "../_components/header";
import TableGrid from "../_components/tableGrid";
import { Button } from "../_components/ui/button";
import { useRouter } from "next/navigation";
import formsServices from "../services/ContactsService";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
} from "../pagination";

const columns = [
  { head: "Aluno", accessor: "student_name" },
  { head: "Data de Nascimento", accessor: "student_birth_date" },
  { head: "Série", accessor: "student_grade_year" },
  { head: "Turma", accessor: "student_class_name" },
  { head: "Data da Solicitação", accessor: "created_at" },
  { head: "Status", accessor: "status" },
];

export default function Solicitações() {
  const router = useRouter();

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5); 
  const [data, setData] = useState([]);
  const [totalItems, setTotalItems] = useState(0); 
  const [application, setApplication] = useState([]);


  useEffect(() => {
    const applications = async () => {
      const data = await formsServices.listAplications()
      setApplication(data)
    }

    applications()
  }, [])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await formsServices.listFormsByUser();
        const { email } = await formsServices.listUser()

        if (response && typeof response === 'object') {
          const dataArray = Array.isArray(response.data) ? response.data : [response];
          response["dataEmail"] = email
          console.log(response, 'já era pra ter email')
          setData(response);
          setTotalItems(dataArray.length);

          } else {
          console.error('A resposta da API não contém dados válidos:', response);
          setData([]);
          setTotalItems(0);
        }
      } catch (error) {
        setData([]);
        setTotalItems(0);
      }
    };

    fetchData();
}, []);
  
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const currentData = Array.isArray(data) && data.length > 0 
    ? data.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
    : []; 

  const handlePageChange = (page:any) => {
    if (page > 0 && page <= totalPages) { 
      setCurrentPage(page);
    }
  };

  return (
    <>
      <Header />
      <div className="px-5 pt-5 bg-[white] mh-[480px] mt-[72px] mr-[115px] ml-[115px] rounded-[20px] shadow-[0_10px_60px_0_rgba(226,236,249,0.5)]">
        <h2 className="text-xl font-bold">Solicitações</h2>
        <br/>
        {application.map(element => {
          console.log(element?.description)
          if (element?.description == "ATENDIMENTOS") {
            return <button onClick={() => router.push('/persons-responsible')}>
              Nova Solicitação
            </button>
          }
        })}
        <TableGrid columns={columns} data={currentData} />

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

              <PaginationNext disabled={currentPage === totalPages} onClick={() => handlePageChange(currentPage + 1)}>
                <span>Next</span>
              </PaginationNext>
            </PaginationContent>
          </Pagination>
        </div>

        <Button
          variant="link"
          className="mt-4"
        >
          Voltar
        </Button>
      </div>
    </>
  );
}
