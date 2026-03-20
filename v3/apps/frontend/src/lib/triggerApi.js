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

export function createTriggerApi(baseUrl = resolveBackendBaseUrl()) {
  const request = createBackendRequest(baseUrl);

  return {
    async health() {
      return requestJson(request, '/api/triggers/health');
    },
    async getTriggers() {
      return requestJson(request, '/api/triggers');
    },
    async getTrigger(triggerId) {
      return requestJson(request, `/api/triggers/${Number(triggerId)}`);
    },
    async createTrigger(payload) {
      return requestJson(request, '/api/triggers', {
        method: 'POST',
        body: payload,
      });
    },
    async updateTrigger(triggerId, payload) {
      return requestJson(request, `/api/triggers/${Number(triggerId)}`, {
        method: 'PUT',
        body: payload,
      });
    },
    async deleteTrigger(triggerId) {
      return requestJson(request, `/api/triggers/${Number(triggerId)}`, {
        method: 'DELETE',
      });
    },
    async toggleTrigger(triggerId) {
      return requestJson(request, `/api/triggers/${Number(triggerId)}/toggle`, {
        method: 'POST',
      });
    },
    async toggleRuleControl(triggerId) {
      return requestJson(request, `/api/triggers/${Number(triggerId)}/toggle-rule-control`, {
        method: 'POST',
      });
    },
  };
}
