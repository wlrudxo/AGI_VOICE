import { createBackendRequest, resolveBackendBaseUrl } from './backend';

async function readBody(response) {
  const contentType = response.headers.get('content-type') ?? '';

  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function extractErrorMessage(body, status) {
  if (typeof body === 'string' && body.trim()) {
    return body;
  }

  if (body && typeof body === 'object') {
    return body.detail ?? body.message ?? JSON.stringify(body);
  }

  return `Request failed with status ${status}`;
}

async function requestJson(request, path, init = {}) {
  const response = await request(path, {
    ...init,
    headers: {
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...(init.headers ?? {}),
    },
    body: init.body ? JSON.stringify(init.body) : undefined,
  });

  const body = await readBody(response);
  if (!response.ok) {
    throw new Error(extractErrorMessage(body, response.status));
  }

  return body;
}

export function createCarMakerApi(baseUrl = resolveBackendBaseUrl()) {
  const request = createBackendRequest(baseUrl);

  return {
    baseUrl,
    async health() {
      return requestJson(request, '/api/carmaker/health');
    },
    async getStatus() {
      return requestJson(request, '/api/carmaker/status');
    },
    async connect(host, port) {
      return requestJson(request, '/api/carmaker/connect', {
        method: 'POST',
        body: { host, port: Number(port) },
      });
    },
    async disconnect() {
      return requestJson(request, '/api/carmaker/disconnect', {
        method: 'POST',
      });
    },
    async getMonitoring() {
      return requestJson(request, '/api/carmaker/monitoring');
    },
    async setMonitoring(active) {
      return requestJson(request, '/api/carmaker/monitoring', {
        method: 'POST',
        body: { active: Boolean(active) },
      });
    },
    async getTelemetry() {
      return requestJson(request, '/api/carmaker/telemetry');
    },
    async executeCommand(command) {
      return requestJson(request, '/api/carmaker/command', {
        method: 'POST',
        body: { command },
      });
    },
    async getWatchedObjects() {
      return requestJson(request, '/api/carmaker/watched-objects');
    },
    async addWatchedObject(index) {
      return requestJson(request, '/api/carmaker/watched-objects', {
        method: 'POST',
        body: { index: Number(index) },
      });
    },
    async removeWatchedObject(index) {
      return requestJson(request, `/api/carmaker/watched-objects/${Number(index)}`, {
        method: 'DELETE',
      });
    },
    async clearWatchedObjects() {
      return requestJson(request, '/api/carmaker/watched-objects', {
        method: 'DELETE',
      });
    },
  };
}
