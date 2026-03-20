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

export function createSettingsApi(baseUrl = resolveBackendBaseUrl()) {
  const request = createBackendRequest(baseUrl);

  return {
    async getChatSettings() {
      return requestJson(request, '/api/settings/chat');
    },
    async updateChatSettings(payload) {
      return requestJson(request, '/api/settings/chat', {
        method: 'PUT',
        body: payload,
      });
    },
    async getTriggerAiSettings() {
      return requestJson(request, '/api/settings/trigger-ai');
    },
    async updateTriggerAiSettings(payload) {
      return requestJson(request, '/api/settings/trigger-ai', {
        method: 'PUT',
        body: payload,
      });
    },
    async getCharacters() {
      return requestJson(request, '/api/characters');
    },
    async getPromptTemplates() {
      return requestJson(request, '/api/prompt-templates');
    },
  };
}
