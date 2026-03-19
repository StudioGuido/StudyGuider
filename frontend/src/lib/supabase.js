import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = url && key ? createClient(url, key) : null;

/** Use this for backend API calls that require auth (e.g. summaries, flashcards). */
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

/** Headers to send with authenticated backend requests. */
export function authHeaders() {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}
