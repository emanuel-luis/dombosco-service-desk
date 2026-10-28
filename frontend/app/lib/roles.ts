import { FormStatus, ParentForm, Role, STATUS, UserInfo } from "./types";

const ROLES: readonly Role[] = ["admin", "staff", "parent", "user", "visitor"];

// Anything the API does not recognise is treated as the least privileged role.
export function parseRole(value: unknown): Role {
  return ROLES.find((role) => role === value) ?? "visitor";
}

export const canCreateRequest = (role: Role) => role === "parent";

export const isOwner = (form: ParentForm, user: UserInfo | null) =>
  !!user && form.responsible_party?.email === user.email;

// Parents may edit or delete only their own pending requests.
export const canEditOrDelete = (
  role: Role,
  form: ParentForm,
  user: UserInfo | null,
) =>
  role === "parent" && form.status === STATUS.PENDENTE && isOwner(form, user);

// Staff answer pending requests; the API assigns the request on the first answer.
export const canAnswer = (role: Role, form: ParentForm) =>
  role === "staff" && form.status === STATUS.PENDENTE;

// Statuses the user may move the request to. The API still has the final say (409).
export function allowedStatuses(
  role: Role,
  status: FormStatus,
  assignedToUser: boolean,
): FormStatus[] {
  if (role === "admin") {
    return ([0, 1, 2, 3] as FormStatus[]).filter((s) => s !== status);
  }
  if (role === "staff" && assignedToUser && status === STATUS.EM_ANDAMENTO) {
    return [STATUS.FINALIZADO, STATUS.CANCELADO];
  }
  return [];
}

// Comments can be edited or deleted by their author while the request is EM ANDAMENTO.
// The API exposes the author as a string, so match on e-mail or full name.
export function canEditComment(
  author: string,
  status: FormStatus,
  user: UserInfo | null,
): boolean {
  if (!user || status !== STATUS.EM_ANDAMENTO) return false;
  const fullName = `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim();
  const norm = (s: string) => s.trim().toLowerCase();
  return (
    norm(author) === norm(user.email) ||
    (fullName !== "" && norm(author) === norm(fullName))
  );
}
