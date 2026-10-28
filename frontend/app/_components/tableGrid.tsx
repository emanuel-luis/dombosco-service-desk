import React, { useState } from "react";
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
import { api } from "../lib/api";
import { toMessage } from "../lib/errors";
import { canAnswer, canEditOrDelete } from "../lib/roles";
import { ParentForm, Role, STATUS_LABELS, UserInfo } from "../lib/types";

interface Column {
  head: string;
  accessor: string;
}

interface TableProps {
  data: ParentForm[];
  columns: Column[];
  role: Role;
  user: UserInfo | null;
}

const itemsPerPage = 5;

const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString("pt-BR");

const TableGrid: React.FC<TableProps> = ({ columns, data, role, user }) => {
  const [deletedIds, setDeletedIds] = useState<number[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [error, setError] = useState("");
  const router = useRouter();

  const renderCellValue = (column: Column, row: ParentForm) => {
    switch (column.accessor) {
      case "created_at":
        return formatDate(row.created_at);
      case "student_birth_date":
        // a date-only ISO string would shift a day through new Date() in UTC-3
        return row.student_birth_date.split("-").reverse().join("/");
      case "status":
        return STATUS_LABELS[row.status] ?? "N/A";
      case "student_name":
        return (
          <button
            onClick={() => router.push(`/form/${row.id}`)}
            className="text-primary underline"
          >
            {row.student_name}
          </button>
        );
      default:
        return String(row[column.accessor as keyof ParentForm] ?? "");
    }
  };

  const onDelete = async (id: number) => {
    if (!window.confirm("Apagar esta solicitação?")) return;
    setError("");
    try {
      await api.deleteForm(id);
      setDeletedIds((ids) => [...ids, id]);
    } catch (e) {
      setError(toMessage(e));
    }
  };

  const renderAction = (row: ParentForm) => {
    if (canEditOrDelete(role, row, user)) {
      return (
        <button onClick={() => onDelete(row.id)} className="text-destructive underline">
          Apagar
        </button>
      );
    }
    if (canAnswer(role, row) || role === "admin") {
      return (
        <button
          onClick={() => router.push(`/form/${row.id}`)}
          className="text-primary underline"
        >
          {role === "admin" ? "Gerenciar" : "Responder"}
        </button>
      );
    }
    return <span>-</span>;
  };

  const rows = data.filter((row) => !deletedIds.includes(row.id));
  const totalPages = Math.max(1, Math.ceil(rows.length / itemsPerPage));
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = rows.slice(startIndex, startIndex + itemsPerPage);
  const visibleColumns = columns.filter((column) => column.accessor !== "id");

  return (
    <>
      {error && (
        <p role="alert" className="text-destructive text-sm my-2">
          {error}
        </p>
      )}
      <Table>
        <TableCaption></TableCaption>
        <TableHeader>
          <TableRow>
            {visibleColumns.map((column) => (
              <TableHead key={column.accessor}>
                <strong>{column.head}</strong>
              </TableHead>
            ))}
            <TableHead>
              <strong>Ações</strong>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {paginatedData.map((row) => (
            <TableRow key={row.id}>
              {visibleColumns.map((column) => (
                <TableCell key={column.accessor}>
                  {renderCellValue(column, row)}
                </TableCell>
              ))}
              <TableCell>{renderAction(row)}</TableCell>
            </TableRow>
          ))}
          {rows.length === 0 && (
            <TableRow>
              <TableCell colSpan={visibleColumns.length + 1}>
                Nenhuma solicitação encontrada.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {/* Pagination Controls */}
      <div className="flex justify-center items-center mt-4">
        <button
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-muted text-brand-text rounded-lg mr-2"
        >
          Anterior
        </button>
        <span>
          Página {currentPage} de {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-muted text-brand-text rounded-lg ml-2"
        >
          Próxima
        </button>
      </div>
    </>
  );
};

export default TableGrid;
