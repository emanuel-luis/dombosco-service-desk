"use client"; // Indica que este é um componente de cliente
import React, { useEffect, useState } from "react";
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

  useEffect(() => {
    setIsMounted(true); // Define como montado quando o componente é renderizado no cliente
  }, []);

  if (!isMounted) {
    return null; // Retorna null até que o componente esteja montado
  }

  return (
    <Table>
      <TableCaption>Solicitações</TableCaption>
      <TableHeader>
        <TableRow>
          {/* Definindo as colunas diretamente no cabeçalho */}
          <TableHead>Aluno</TableHead>
          <TableHead>Série</TableHead>
          <TableHead>Telefone</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Data</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {columns.map((column) => (
              <TableCell key={column.accessor}>
                {row[column.accessor]}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default TableGrid;
