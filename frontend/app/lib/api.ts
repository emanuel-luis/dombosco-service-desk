import { request } from "./client";
import {
  Application,
  Choices,
  Comment,
  FormStatus,
  LoginResponse,
  ParentForm,
  ParentFormInput,
  RegisterInput,
  StaffForm,
  StaffFormInput,
  UserInfo,
} from "./types";

const BAD_LOGIN = "E-mail ou senha incorretos.";

export const api = {
  login: (email: string, password: string) =>
    request<LoginResponse>("POST", "/auth/login/", {
      auth: false,
      body: { email, password },
      messages: { 400: BAD_LOGIN, 401: BAD_LOGIN },
    }),

  register: (values: RegisterInput) =>
    request<unknown>("POST", "/auth/registration/", {
      auth: false,
      body: values,
      messages: {
        400: "Não foi possível criar a conta. Verifique os dados: o e-mail pode já estar em uso ou a senha ser fraca.",
      },
    }),

  getUser: () => request<UserInfo>("GET", "/auth/user/"),

  listApplications: () => request<Application[]>("GET", "/core/applications/"),

  listForms: (query?: { assigned_staff?: string; status?: number }) =>
    request<ParentForm[]>("GET", "/forms/parent/", { query }),
  getForm: (id: number | string) =>
    request<ParentForm>("GET", "/forms/parent/", { query: { id } }),
  getChoices: () => request<Choices>("GET", "/forms/parent/choices/"),
  createForm: (input: ParentFormInput) =>
    request<ParentForm>("POST", "/forms/parent/", { body: input }),
  updateForm: (id: number, input: ParentFormInput) =>
    request<ParentForm>("PUT", "/forms/parent/", { query: { id }, body: input }),
  deleteForm: (id: number) =>
    request<unknown>("DELETE", "/forms/parent/", { query: { id } }),
  updateStatus: (id: number, status: FormStatus) =>
    request<unknown>("PUT", "/forms/parent/update-status/", {
      query: { id },
      body: { status },
    }),

  listStaffForms: () => request<StaffForm[]>("GET", "/forms/staff/"),
  createStaffForm: (input: StaffFormInput) =>
    request<StaffForm>("POST", "/forms/staff/", { body: input }),

  listComments: (formId: number) =>
    request<Comment[]>("GET", "/forms/comment/", { query: { id: formId } }),
  createComment: (formId: number, comment: string) =>
    request<Comment>("POST", "/forms/comment/", {
      body: { parent_form_id: formId, comment },
    }),
  updateComment: (id: number, comment: string) =>
    request<Comment>("PUT", "/forms/comment/", { query: { id }, body: { comment } }),
  deleteComment: (id: number) =>
    request<unknown>("DELETE", "/forms/comment/", { query: { id } }),
};
