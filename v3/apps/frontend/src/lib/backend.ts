const FALLBACK_BACKEND_URL = 'http://127.0.0.1:8010';

declare global {
  interface Window {
    __V3_BACKEND_URL__?: string;
    __AGI_VOICE_V3_BACKEND_URL__?: string;
    desktop?: {
      backend?: {
        baseUrl?: string;
      };
      backendUrl?: string;
    };
  }
}

function normalizeUrl(value: unknown): string | null {
  if (typeof value !== 'string') {
    return null;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  return trimmed.replace(/\/+$/, '');
}

function readPath(root: unknown, path: string[]): string | null {
  let current: unknown = root;

  for (const key of path) {
    if (current == null || typeof current !== 'object') {
      return null;
    }
    current = (current as Record<string, unknown>)[key];
  }

  return typeof current === 'string' ? current : null;
}

export function resolveBackendBaseUrl(): string {
  const windowUrl =
    typeof window === 'undefined'
      ? null
      : normalizeUrl(
          readPath(window, ['desktop', 'backend', 'baseUrl']) ??
            readPath(window, ['desktop', 'backendUrl']) ??
            window.__V3_BACKEND_URL__ ??
            window.__AGI_VOICE_V3_BACKEND_URL__
        );

  if (windowUrl) {
    return windowUrl;
  }

  const envUrl = normalizeUrl(import.meta.env.VITE_V3_BACKEND_URL);
  if (envUrl) {
    return envUrl;
  }

  return FALLBACK_BACKEND_URL;
}

type JsonInit = Omit<RequestInit, 'body'> & {
  body?: unknown;
};

export async function requestJson<T>(path: string, init: JsonInit = {}): Promise<T> {
  const baseUrl = resolveBackendBaseUrl();
  const url = new URL(path, `${baseUrl}/`);
  const response = await fetch(url, {
    cache: 'no-store',
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init.body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(init.headers ?? {}),
    },
    body: init.body !== undefined ? JSON.stringify(init.body) : undefined,
  });

  const contentType = response.headers.get('content-type') ?? '';
  const body = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof body === 'string'
        ? body
        : (body as Record<string, unknown>)?.detail ??
          (body as Record<string, unknown>)?.message ??
          `Request failed with status ${response.status}`;
    throw new Error(String(message));
  }

  return body as T;
}
