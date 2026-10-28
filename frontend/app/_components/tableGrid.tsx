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

interface TableProps {
  data: any[];
  columns: any[];
  email: any[];
}

const TableGrid: React.FC<TableProps> = ({ columns, data, email }) => {
  const [tableData, setTableData] = useState(data); 
  const [isMounted, setIsMounted] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [userStaff, setUserStaff] = useState(false);
  const itemsPerPage = 5;
  const router = useRouter();

  const formatDate = (dateString: any) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR");
  };

  useEffect(() => {
    setIsMounted(true);
    const getUserInfo = async () => {
      const apps = await formsServices.listAplications();
      const containsGroup2 = apps.some(
        (app: any) => app.groups && app.groups.length === 1 && app.groups[0] === 2
      );

      if (containsGroup2) {
        setUserStaff(true);
      }
    };

    getUserInfo();
  }, []);

  const renderCellValue = (column: Column, row: Row) => {
    const statusText = ["Pendente", "Em andamento", "Finalizado", "Cancelado"];
    const renderMap: Record<string, () => any> = {
      created_at: () => formatDate(row[column.accessor]),
      status: () => statusText[row["status"]] || "N/A",
      student_name: () => (
        <button
          onClick={() => {
            router.push(`/form/${row?.id}`);
          }}
          className="text-blue-500 underline"
        >
          {row[column.accessor]}
        </button>
      ),
    };

    return renderMap[column.accessor]
      ? renderMap[column.accessor]()
      : row[column.accessor];
  };

  const onDelete = async (id: number) => {
    await formsServices.deleteForms(id);
    setTableData((prevData) => prevData.filter((row) => row.id !== id)); // Filter out deleted item
  };

  const filteredData = userStaff
    ? tableData
    : tableData.filter((row) => row.responsible_party?.email === email);
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, endIndex);

  if (!isMounted) {
    return null;
  }

  console.log(userStaff);

  return (
    <>
      <Table>
        <TableCaption></TableCaption>
        <TableHeader>
          <TableRow>
            {columns
              .filter((column) => column.accessor !== "id")
              .map((column) => (
                <TableHead key={column.accessor}>
                  <strong>{column.head}</strong>
                </TableHead>
              ))}
            {!userStaff ? (
              <TableHead>
                <strong>Apagar</strong>
              </TableHead>
            ) : (
              <TableHead>
                <strong>Responder</strong>
              </TableHead>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {paginatedData.map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {columns
                .filter((column) => column.accessor !== "id")
                .map((column) => (
                  <TableCell key={column.accessor}>
                    {renderCellValue(column, row)}
                  </TableCell>
                ))}
              {!userStaff && row.status === 0 ? (
                <TableCell>
                  <button
                    onClick={() => onDelete(row?.id)}
                    className="text-red-500 underline"
                  >
                    Delete
                  </button>
                </TableCell>
              ) : userStaff && row.status !== 2 && row.status !== 3 ? (
                <TableCell>
                  <button
                    onClick={() => {
                      router.push(`/form/${row?.id}`);
                    }}
                    className="text-blue-500 underline"
                  >
                    Responder
                  </button>
                </TableCell>
              ) : (
                <TableCell>
                  <span>-</span>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Pagination Controls */}
      <div className="flex justify-center items-center mt-4">
        <button
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg mr-2"
        >
          Anterior
        </button>
        <span>
          Página {currentPage} de {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
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
