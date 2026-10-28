export type Role = "admin" | "staff" | "parent" | "user" | "visitor";

export type FormStatus = 0 | 1 | 2 | 3;

export const STATUS = {
  PENDENTE: 0,
  EM_ANDAMENTO: 1,
  FINALIZADO: 2,
  CANCELADO: 3,
} as const;

export const STATUS_LABELS: Record<FormStatus, string> = {
  0: "Pendente",
  1: "Em andamento",
  2: "Finalizado",
  3: "Cancelado",
};

export interface UserInfo {
  pk: number;
  email: string;
  first_name?: string;
  last_name?: string;
  groups: string[];
  role: Role;
}

export interface UserProfile {
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  mobile_phone: string;
}

export interface ParentForm {
  id: number;
  responsible_party: UserProfile;
  requested_by: number;
  student_name: string;
  student_birth_date: string;
  student_grade_year: number;
  student_class_name: string;
  relationship_to_student: number;
  issue_description: string;
  status: FormStatus;
  created_at: string;
  updated_at: string;
}

export type ParentFormInput = Omit<
  ParentForm,
  "id" | "responsible_party" | "status" | "created_at" | "updated_at"
>;

export interface StaffForm {
  id: number;
  assigned_staff: UserProfile;
  school_advice: string | null;
  actions_taken: string | null;
  final_notes: string | null;
  parent_form_id: number;
  created_at: string;
  updated_at: string;
}

export interface StaffFormInput {
  parent_form_id: number;
  school_advice: string;
  actions_taken: string;
  final_notes: string;
}

export interface Comment {
  id: number;
  user: string;
  user_id: number;
  parent_form_id: number;
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: number;
  mdm_id: string;
  name: string;
  description: string | null;
  groups: number[];
}

export interface Choices {
  relationship: Record<string, string>;
  status?: Record<string, string>;
  required_by?: Record<string, string>;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: UserInfo;
}

export interface RegisterInput {
  email: string;
  password1: string;
  password2: string;
  first_name: string;
  last_name: string;
  mobile_phone?: string;
}
