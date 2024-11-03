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
import { useRouter } from "next/navigation";

interface Column {
  accessor: string;
}

interface Row {
  [key: string]: any; // Pode ser ajustado para tipos mais específicos, se necessário
}

interface Status {
  [key: string]: any; // Ou você pode definir um tipo específico se conhecer as chaves
}

interface Column {
  Header: string;
  accessor: string;
}

interface Data {
  [key: string]: string; // Permite qualquer chave como string
}

interface TableProps {
  data: any[];
  columns: any[];
}


const TableGrid: React.FC<TableProps> = ({ columns, data }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [status, setStatus] = useState<Status[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<Row | null>(null);
  const router = useRouter()

  const formatDate = (dateString: any) => {
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

  const renderCellValue = (column: Column, row: Row) => {
    const statusText = ["Pendente", "Em andamento", "Finalizado", "Cancelado"]
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

    console.log(data)
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
          {columns.map((column) => (
             <TableHead key={column.accessor}><strong>{column.head}</strong></TableHead>
          ))}
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
        <hr />
      </TableBody>
    </Table>

  );
};

export default TableGrid;

