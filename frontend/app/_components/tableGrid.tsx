"use client";
import React, { useEffect, useState } from "react";
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
import { useRouter } from "next/navigation";

interface Column {
  Header: string;
  accessor: string;
}

interface Row {
  [key: string]: any;
}

interface Status {
  [key: string]: any;
}

interface TableProps {
  data: any[];
  columns: any[];
  email: any[];
}

const TableGrid: React.FC<TableProps> = ({ columns, data, email }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [status, setStatus] = useState<Status[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5; // Número de itens por página
  const router = useRouter();

  const formatDate = (dateString: any) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR");
  };

  useEffect(() => {
    setIsMounted(true);
    formsServices.listStatus()
      .then(response => {
        setStatus(response);
      })
      .catch(error => {
        console.error("Error fetching status:", error);
      });
  }, []);

  const renderCellValue = (column: Column, row: Row) => {
    const statusText = ["Pendente", "Em andamento", "Finalizado", "Cancelado"];
    const renderMap: Record<string, () => any> = {
      created_at: () => formatDate(row[column.accessor]),
      status: () => statusText[row['status']] || 'N/A',
      student_name: () => (
        <button
          onClick={(e) => {
            router.push(`/form/${e.target?.innerText}`)
          }} 
          className="text-blue-500 underline"
        >
          {row[column.accessor]}
        </button>
      ),
    };

    return renderMap[column.accessor] ? renderMap[column.accessor]() : row[column.accessor];
  };

  // Função de paginação
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = data.filter(row => row.responsible_party?.email === email).slice(startIndex, endIndex);

  const totalPages = Math.ceil(data.length / itemsPerPage);

  if (!isMounted) {
    return null;
  }

  return (
    <>
      <Table>
        <TableCaption></TableCaption>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={column.accessor}>
                <strong>{column.head}</strong>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {paginatedData.map((row, rowIndex) => (
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

      {/* Controles de Paginação */}
      <div className="flex justify-center items-center mt-4">
        <button
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg mr-2"
        >
          Anterior
        </button>
        <span>Página {currentPage} de {totalPages}</span>
        <button
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg ml-2"
        >
          Próxima
        </button>
      </div>
    </>
  );
};

export default TableGrid;
