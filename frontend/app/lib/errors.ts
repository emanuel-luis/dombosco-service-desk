const MESSAGES: Record<number, string> = {
  400: "Dados inválidos. Revise os campos e tente novamente.",
  401: "Sua sessão expirou. Entre novamente.",
  403: "Você não tem permissão para realizar esta ação.",
  404: "Não encontrado, ou você não tem acesso a este item.",
  409: "Esta ação não é permitida no estado atual da solicitação.",
};

export const NETWORK_MESSAGE =
  "Não foi possível conectar ao servidor. Tente novamente em instantes.";
const SERVER_MESSAGE = "Erro no servidor. Tente novamente em instantes.";
const UNKNOWN_MESSAGE = "Ocorreu um erro inesperado. Tente novamente.";

// status 0 means the request never reached the server.
export function messageForStatus(status: number): string {
  if (status === 0) return NETWORK_MESSAGE;
  if (MESSAGES[status]) return MESSAGES[status];
  if (status >= 500) return SERVER_MESSAGE;
  return UNKNOWN_MESSAGE;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message?: string,
  ) {
    super(message ?? messageForStatus(status));
    this.name = "ApiError";
  }
}

export function toMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : UNKNOWN_MESSAGE;
}
