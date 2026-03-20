const FALLBACK_BACKEND_URL = 'http://127.0.0.1:8010';

function normalizeUrl(value) {
  if (typeof value !== 'string') {
    return null;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  return trimmed.replace(/\/+$/, '');
}

function readPath(root, path) {
  let current = root;

  for (const key of path) {
    if (current == null) {
      return null;
    }

    current = current[key];
  }

  return typeof current === 'string' ? current : null;
}

export function resolveBackendConfig() {
  const windowUrl =
    typeof window === 'undefined'
      ? null
      : normalizeUrl(
          readPath(window, ['desktop', 'backend', 'baseUrl']) ??
            readPath(window, ['desktop', 'backendUrl']) ??
            window.__V3_BACKEND_URL__ ??
            window.__AGI_VOICE_V3_BACKEND_URL__ ??
            readPath(window, ['process', 'env', 'V3_BACKEND_URL']) ??
            readPath(window, ['process', 'env', 'VITE_V3_BACKEND_URL'])
        );

  if (windowUrl) {
    return {
      baseUrl: windowUrl,
      source: 'electron',
    };
  }

  const envUrl = normalizeUrl(import.meta.env.VITE_V3_BACKEND_URL);
  if (envUrl) {
    return {
      baseUrl: envUrl,
      source: 'vite-env',
    };
  }

  return {
    baseUrl: FALLBACK_BACKEND_URL,
    source: 'fallback',
  };
}

export function resolveBackendBaseUrl() {
  return resolveBackendConfig().baseUrl;
}

export function resolveBackendSource() {
  return resolveBackendConfig().source;
}

export function createBackendRequest(baseUrl = resolveBackendBaseUrl()) {
  const resolvedBaseUrl = normalizeUrl(baseUrl) ?? FALLBACK_BACKEND_URL;

  return async function request(path, init = {}) {
    const url = new URL(path, `${resolvedBaseUrl}/`);
    return fetch(url, {
      cache: 'no-store',
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init.headers ?? {}),
      },
    });
  };
}
