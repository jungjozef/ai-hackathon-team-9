const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "auth_token";

const DEFAULT_TIMEOUT_MS = 8000;

async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
}

function getStoredToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setStoredToken(token: string): void {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // ignore storage errors
  }
}

function clearStoredToken(): void {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // ignore storage errors
  }
}

function authHeaders(): HeadersInit {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface ApiDepartment {
  name: string;
  icon: string;
  description: string;
}

export interface ApiUser {
  id: number;
  email: string;
  name: string;
  picture_url: string | null;
  created_at: string | null;
  last_login: string | null;
}

export interface ApiDocument {
  id: number;
  title: string;
  content: string;
  upload_date: string | null;
  tags: string;
  metadata: string;
}

export interface ChatHistoryItem {
  role: "user" | "assistant";
  content: string;
}

export async function fetchDepartments(): Promise<ApiDepartment[]> {
  const resp = await fetchWithTimeout(`${API_URL}/departments`);
  if (!resp.ok) {
    throw new Error(`Failed to load departments (${resp.status})`);
  }
  return resp.json();
}

export async function fetchAuthUrl(): Promise<string> {
  const resp = await fetchWithTimeout(`${API_URL}/auth/google/login`);
  if (!resp.ok) {
    throw new Error(`Failed to start login (${resp.status})`);
  }
  const data = await resp.json();
  return data.authorization_url as string;
}

export async function fetchMe(): Promise<ApiUser> {
  const resp = await fetchWithTimeout(`${API_URL}/auth/me`, {
    headers: authHeaders(),
  });
  if (!resp.ok) {
    throw new Error(`Failed to fetch user (${resp.status})`);
  }
  return resp.json();
}

export async function fetchDocuments(): Promise<ApiDocument[]> {
  const resp = await fetchWithTimeout(`${API_URL}/documents`, {
    headers: authHeaders(),
  });
  if (!resp.ok) {
    if (resp.status === 401) {
      throw new Error("Not authenticated. Please sign in.");
    }
    throw new Error(`Failed to load documents (${resp.status})`);
  }
  return resp.json();
}

export async function uploadDocument(file: File): Promise<ApiDocument> {
  const formData = new FormData();
  formData.append("file", file);

  const resp = await fetchWithTimeout(`${API_URL}/upload/document`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(detail || `Upload failed (${resp.status})`);
  }
  return resp.json();
}

export async function deleteDocument(docId: number): Promise<void> {
  const resp = await fetchWithTimeout(`${API_URL}/documents/${docId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!resp.ok) {
    if (resp.status === 401) {
      throw new Error("Not authenticated. Please sign in.");
    }
    throw new Error(`Failed to delete document (${resp.status})`);
  }
}

export async function sendChat(
  department: string,
  message: string,
  history: ChatHistoryItem[]
): Promise<string> {
  const resp = await fetchWithTimeout(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ department, message, history }),
  });
  if (!resp.ok) {
    const detail = await resp.text();
    if (resp.status === 401) {
      throw new Error("Not authenticated. Please sign in.");
    }
    throw new Error(detail || `Chat failed (${resp.status})`);
  }
  const data = await resp.json();
  return data.reply as string;
}

export const authStorage = {
  getToken: getStoredToken,
  setToken: setStoredToken,
  clearToken: clearStoredToken,
};
