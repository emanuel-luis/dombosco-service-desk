// Build-time settings. Next inlines NEXT_PUBLIC_* values, so they must be
// read as literal property accesses.
const trimSlash = (value: string) => value.replace(/\/+$/, "");

export const API_URL = trimSlash(process.env.NEXT_PUBLIC_API_URL ?? "");

export const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";
export const GOOGLE_REDIRECT_URI =
  process.env.NEXT_PUBLIC_GOOGLE_REDIRECT_URI ?? "";

export const GOOGLE_ENABLED =
  GOOGLE_CLIENT_ID !== "" && GOOGLE_REDIRECT_URI !== "";
