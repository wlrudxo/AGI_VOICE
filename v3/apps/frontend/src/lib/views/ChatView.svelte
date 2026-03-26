<script>
  import { onMount } from 'svelte';
  import { marked } from 'marked';
  import { parseWithSegments } from '../actions/parser.js';
  import { createChatApi } from '../chatApi.js';
  import { createSettingsApi } from '../settingsApi.js';

  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  const chatApi = createChatApi();
  const settingsApi = createSettingsApi();

  let messages = $state([]);
  let inputMessage = $state('');
  let isLoading = $state(false);
  let messagesContainer = $state();
  let conversationId = $state(null);
  let characterId = $state(null);
  let promptTemplateId = $state(null);
  let claudeModel = $state('sonnet');
  let settingsLoaded = $state(false);

  function clearConversation() {
    conversationId = null;
    messages = [];
  }

  function preprocessMarkdown(content) {
    const parts = [];
    let inCodeBlock = false;
    let inInlineCode = false;
    let currentPart = '';

    for (let i = 0; i < content.length; i += 1) {
      const char = content[i];
      const nextChars = content.slice(i, i + 3);

      if (nextChars === '```') {
        parts.push(currentPart);
        currentPart = '```';
        inCodeBlock = !inCodeBlock;
        i += 2;
        continue;
      }

      if (char === '`' && !inCodeBlock) {
        parts.push(currentPart);
        currentPart = '`';
        inInlineCode = !inInlineCode;
        continue;
      }

      if (!inCodeBlock && !inInlineCode) {
        if (char === '<') {
          currentPart += '&lt;';
          continue;
        }
        if (char === '>') {
          currentPart += '&gt;';
          continue;
        }
      }

      currentPart += char;
    }

    parts.push(currentPart);
    return parts.join('');
  }

  function getUserInfo() {
    try {
      return localStorage.getItem('agi_voice_user_info') || '';
    } catch {
      return '';
    }
  }

  function getUserName() {
    try {
      return localStorage.getItem('agi_voice_user_name') || '';
    } catch {
      return '';
    }
  }

  function getFinalMessage() {
    try {
      return localStorage.getItem('agi_voice_final_message') || '';
    } catch {
      return '';
    }
  }

  async function loadChatSettings() {
    try {
      const settings = await settingsApi.getChatSettings();
      characterId = settings.defaultCharacterId;
      promptTemplateId = settings.defaultPromptTemplateId;
      claudeModel = settings.defaultClaudeModel || 'sonnet';

      if (!characterId || !promptTemplateId) {
        messages = [
          ...messages,
          {
            role: 'error',
            content:
              '채팅 설정이 되어있지 않습니다. 설정 화면에서 캐릭터와 템플릿을 선택해주세요.',
            timestamp: new Date(),
          },
        ];
      }
    } catch {
      messages = [
        ...messages,
        {
          role: 'error',
          content: '채팅 설정을 불러오는데 실패했습니다.',
          timestamp: new Date(),
        },
      ];
    } finally {
      settingsLoaded = true;
    }
  }

  function formatTime(date) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  function shouldShowTime(index) {
    if (index === messages.length - 1) {
      return true;
    }
    return messages[index].role !== messages[index + 1]?.role;
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }

  function appendAssistantResponse(rawResponse) {
    const segments = parseWithSegments(rawResponse);
    const timestamp = new Date();
    for (const segment of segments) {
      if (segment.type === 'text') {
        messages = [
          ...messages,
          {
            role: 'assistant',
            content: segment.content,
            timestamp,
          },
        ];
      } else if (segment.type === 'action') {
        messages = [
          ...messages,
          {
            role: 'action',
            label: segment.label,
            timestamp,
          },
        ];
      }
    }
  }

  async function loadConversation(selectedId) {
    try {
      const conversation = await chatApi.getConversation(selectedId);
      const messagesData = await chatApi.getConversationMessages(selectedId, 50);

      conversationId = selectedId;
      characterId = conversation.characterId;
      promptTemplateId = conversation.promptTemplateId;

      const parsedMessages = [];
      for (const message of messagesData) {
        const timestamp = message.createdAt ? new Date(message.createdAt) : new Date();
        if (message.role === 'assistant') {
          const segments = parseWithSegments(message.content);
          for (const segment of segments) {
            if (segment.type === 'text') {
              parsedMessages.push({
                role: 'assistant',
                content: segment.content,
                timestamp,
              });
            } else if (segment.type === 'action') {
              parsedMessages.push({
                role: 'action',
                label: segment.label,
                timestamp,
              });
            }
          }
        } else {
          parsedMessages.push({
            role: message.role,
            content: message.content,
            timestamp,
          });
        }
      }

      messages = parsedMessages;
      scrollToBottom();
    } catch (error) {
      messages = [
        ...messages,
        {
          role: 'error',
          content: error instanceof Error ? error.message : '대화를 불러오는데 실패했습니다.',
          timestamp: new Date(),
        },
      ];
    }
  }

  function handleSelectConversation(event) {
    const selectedId = event.detail?.conversationId ?? null;
    if (selectedId === null) {
      clearConversation();
      return;
    }
    loadConversation(selectedId);
  }

  async function sendMessage() {
    const userMessage = inputMessage.trim();
    if (!userMessage || isLoading) {
      return;
    }

    if (!settingsLoaded || !characterId || !promptTemplateId) {
      messages = [
        ...messages,
        {
          role: 'error',
          content: '채팅 설정을 먼저 완료해주세요.',
          timestamp: new Date(),
        },
      ];
      return;
    }

    messages = [
      ...messages,
      {
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      },
    ];
    inputMessage = '';
    isLoading = true;
    scrollToBottom();

    try {
      const requestBody = {
        message: userMessage,
        model: claudeModel,
        userName: getUserName(),
        role: 'user',
      };

      if (conversationId) {
        requestBody.conversationId = conversationId;
      } else {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        requestBody.characterId = characterId;
        requestBody.promptTemplateId = promptTemplateId;
        requestBody.userInfo = getUserInfo();
        requestBody.finalMessage = getFinalMessage();
        requestBody.title = `${year}.${month}.${day}. ${hours}:${minutes}`;
      }

      const data = await chatApi.chat(requestBody);
      if (!conversationId && data.conversationId > 0) {
        conversationId = data.conversationId;
        window.dispatchEvent(
          new CustomEvent('conversationCreated', {
            detail: { conversationId: data.conversationId },
          })
        );
      }

      const rawResponse = data.responses?.[0];
      if (rawResponse) {
        appendAssistantResponse(rawResponse);
      } else {
        messages = [
          ...messages,
          {
            role: 'error',
            content: '빈 응답을 받았습니다.',
            timestamp: new Date(),
          },
        ];
      }
    } catch (error) {
      messages = [
        ...messages,
        {
          role: 'error',
          content: error instanceof Error ? error.message : '오류가 발생했습니다. 다시 시도해주세요.',
          timestamp: new Date(),
        },
      ];
    } finally {
      isLoading = false;
      scrollToBottom();
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  $effect(() => {
    loadChatSettings();
  });

  onMount(() => {
    window.addEventListener('selectConversation', handleSelectConversation);
    return () => {
      window.removeEventListener('selectConversation', handleSelectConversation);
    };
  });
</script>

<div class="chat-view">
  <div class="messages-container" bind:this={messagesContainer}>
    {#if messages.length === 0}
      <div class="empty-state">
        <p>AI 채팅을 시작해보세요.</p>
      </div>
    {:else}
      {#each messages as message, index}
        {#if message.role === 'user'}
          <div class="message-wrapper message-wrapper-user">
            {#if shouldShowTime(index)}
              <span class="message-time message-time-user">{formatTime(message.timestamp)}</span>
            {/if}
            <div class="message message-user">
              <div class="message-content">
                <p>{message.content}</p>
              </div>
            </div>
          </div>
        {/if}

        {#if message.role === 'action'}
          <div class="message message-action">
            <div class="message-content">
              <div class="action-indicator">{message.label}</div>
            </div>
          </div>
        {/if}

        {#if message.role === 'assistant'}
          <div class="message-wrapper message-wrapper-assistant">
            <div class="message message-assistant">
              <div class="message-content">
                <div class="markdown-content">{@html marked(preprocessMarkdown(message.content))}</div>
              </div>
            </div>
            {#if shouldShowTime(index)}
              <span class="message-time message-time-assistant">{formatTime(message.timestamp)}</span>
            {/if}
          </div>
        {/if}

        {#if message.role === 'error'}
          <div class="message-wrapper message-wrapper-user">
            {#if shouldShowTime(index)}
              <span class="message-time message-time-user">{formatTime(message.timestamp)}</span>
            {/if}
            <div class="message message-error">
              <div class="message-content">
                <p>{message.content}</p>
              </div>
            </div>
          </div>
        {/if}
      {/each}

      {#if isLoading}
        <div class="message message-assistant">
          <div class="message-content">
            <div class="loading">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <div class="input-container">
    <input
      type="text"
      bind:value={inputMessage}
      onkeydown={handleKeydown}
      placeholder="메시지를 입력하세요..."
      disabled={isLoading}
    />
    <button class="btn-primary" onclick={sendMessage} disabled={!inputMessage.trim() || isLoading}>
      {#if isLoading}
        ⏳
      {:else}
        전송
      {/if}
    </button>
  </div>
</div>

<style>
  .chat-view {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--color-text-muted);
  }

  .message-wrapper {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    gap: 0.25rem;
    max-width: 80%;
  }

  .message-wrapper-user {
    align-self: flex-end;
  }

  .message-wrapper-assistant {
    align-self: flex-start;
  }

  .message-user .message-content {
    background: var(--color-chat-user-bg);
    color: white;
    border-radius: 12px 12px 4px 12px;
  }

  .message-assistant .message-content {
    background: var(--color-chat-assistant-bg);
    color: var(--color-text-primary);
    border-radius: 12px 12px 12px 4px;
    border: 1px solid var(--color-border);
  }

  .message-error .message-content {
    background: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fecaca;
    border-radius: 12px;
  }

  .message-action .message-content {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 999px;
    padding: 0.4rem 0.75rem;
    font-size: 0.85rem;
    align-self: center;
  }

  .message-content {
    padding: 0.75rem 1rem;
    line-height: 1.55;
    word-break: break-word;
  }

  .message-content p {
    margin: 0;
  }

  .message-time {
    font-size: 0.72rem;
    color: var(--color-text-muted);
    white-space: nowrap;
  }

  .markdown-content :global(p:first-child) {
    margin-top: 0;
  }

  .markdown-content :global(p:last-child) {
    margin-bottom: 0;
  }

  .markdown-content :global(pre) {
    overflow-x: auto;
    padding: 0.75rem;
    border-radius: 8px;
    background: #0f172a;
    color: #e2e8f0;
  }

  .markdown-content :global(code) {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }

  .input-container {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    border-top: 1px solid var(--color-border);
    background: var(--color-surface);
  }

  .input-container input {
    flex: 1;
    min-width: 0;
  }

  .loading {
    display: flex;
    gap: 0.35rem;
    align-items: center;
  }

  .dot {
    width: 0.45rem;
    height: 0.45rem;
    border-radius: 999px;
    background: var(--color-text-muted);
    animation: pulse 1s infinite ease-in-out;
  }

  .dot:nth-child(2) {
    animation-delay: 0.15s;
  }

  .dot:nth-child(3) {
    animation-delay: 0.3s;
  }

  @keyframes pulse {
    0%,
    80%,
    100% {
      opacity: 0.3;
      transform: translateY(0);
    }

    40% {
      opacity: 1;
      transform: translateY(-2px);
    }
  }
</style>
