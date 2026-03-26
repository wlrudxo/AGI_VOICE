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

export function createChatApi(baseUrl = resolveBackendBaseUrl()) {
  const request = createBackendRequest(baseUrl);

  return {
    async chat(payload) {
      return requestJson(request, '/api/chat', {
        method: 'POST',
        body: payload,
      });
    },
    async getConversations() {
      return requestJson(request, '/api/conversations');
    },
    async getConversation(conversationId) {
      return requestJson(request, `/api/conversations/${conversationId}`);
    },
    async getConversationMessages(conversationId, limit = 50) {
      return requestJson(
        request,
        `/api/conversations/${conversationId}/messages?limit=${limit}`
      );
    },
    async updateConversation(conversationId, payload) {
      return requestJson(request, `/api/conversations/${conversationId}`, {
        method: 'PUT',
        body: payload,
      });
    },
    async deleteConversation(conversationId) {
      return requestJson(request, `/api/conversations/${conversationId}`, {
        method: 'DELETE',
      });
    },
  };
}
