"use client"; // Indica que este é um componente de cliente
import React, { useEffect, useState } from "react";
// import providers from "../services/apiProvider";
import formsServices from "../services/ContactsService";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../_components/ui/table";


interface Column {
  Header: string;
  accessor: string;
}

interface Data {
  [key: string]: string; // Permite qualquer chave como string
}

const TableGrid = ({ columns, data }: { columns: Column[]; data: Data[] }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [status, setStatus] = useState([]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR");
  };

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    formsServices.listStatus()
      .then(response => {
        setStatus(response);
      })
      .catch(error => {
        console.error("Error fetching status:", error);
      });
  }, []);

  const renderCellValue = (column, row) => {
    const renderMap = {
      created_at: () => formatDate(row[column.accessor]),
      status: () => status['status']?.[row[column.accessor]]
    };
  
    return renderMap[column.accessor] ? renderMap[column.accessor]() : row[column.accessor];
  };
  

  if (!isMounted) {
    return null;
  }
  
  return (
    <Table>
      <TableCaption></TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Aluno</TableHead>
          <TableHead>Data de Nascimento</TableHead>
          <TableHead>Série</TableHead>
          <TableHead>Turma</TableHead>
          <TableHead>Data da Solicitação</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {columns.map((column) => (
              <TableCell key={column.accessor}>
                {renderCellValue(column, row)}

              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default TableGrid;
