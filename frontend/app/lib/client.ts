import { API_URL } from "./config";
import { ApiError, messageForStatus } from "./errors";

type Query = Record<string, string | number | undefined>;

export interface RequestOptions {
  query?: Query;
  body?: unknown;
  // Login and registration are called without a token and must not redirect on 401.
  auth?: boolean;
  // Per-call pt-BR messages that replace the generic ones.
  messages?: Partial<Record<number, string>>;
}

const TOKEN_KEY = "token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // storage blocked: the session lasts only until the next request fails
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // nothing to clear
  }
}

export function buildUrl(
  path: string,
  query: Query = {},
  base = API_URL,
): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value));
  }
  const qs = params.toString();
  return `${base}/api/v1${path}${qs ? `?${qs}` : ""}`;
}

function redirectToLogin() {
  clearToken();
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- full reload on purpose: drops all client state
    window.location.assign("/login");
  }
}

export async function request<T>(
  method: "GET" | "POST" | "PUT" | "DELETE",
  path: string,
  { query, body, auth = true, messages }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = auth ? getToken() : null;
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, messages?.[0]);
  }

  if (!response.ok) {
    if (response.status === 401 && auth) redirectToLogin();
    throw new ApiError(
      response.status,
      messages?.[response.status] ?? messageForStatus(response.status),
    );
  }

  const text = await response.text();
  return (text ? JSON.parse(text) : undefined) as T;
}
