<script lang="ts">
	import Icon from '@iconify/svelte';
	import { marked } from 'marked';
	import type { ChatMessage } from '$lib/chat/types';

	let {
		messages = [],
		isLoading = false,
		collapsedVehicleData = {},
		onToggleVehicleData = (_index: number) => {}
	}: {
		messages: ChatMessage[];
		isLoading: boolean;
		collapsedVehicleData: Record<number, boolean>;
		onToggleVehicleData: (index: number) => void;
	} = $props();

	marked.setOptions({
		breaks: true,
		gfm: true
	});

	function preprocessMarkdown(content: string) {
		const parts: string[] = [];
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

	function parseSystemMessage(content: string) {
		const vehicleDataMatch = content.match(/## Current Vehicle Data:\n([\s\S]*?)(?=\n##|$)/);

		if (vehicleDataMatch) {
			const vehicleData = vehicleDataMatch[1].trim();
			const vehicleDataCount = vehicleData.split('\n').filter((line) => line.trim()).length;
			const otherContent = content
				.replace(/## Current Vehicle Data:\n[\s\S]*?(?=\n##|$)/, '')
				.trim();
			return { vehicleData, vehicleDataCount, otherContent };
		}

		return { vehicleData: null, vehicleDataCount: 0, otherContent: content };
	}

	function formatTime(date: Date) {
		const hours = date.getHours().toString().padStart(2, '0');
		const minutes = date.getMinutes().toString().padStart(2, '0');
		return `${hours}:${minutes}`;
	}

	function shouldShowTime(index: number) {
		if (index === messages.length - 1) return true;
		return messages[index].role !== messages[index + 1]?.role;
	}
</script>

{#if messages.length === 0}
	<div class="empty-state"></div>
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

		{#if message.role === 'system'}
			{@const parsed = parseSystemMessage(message.content || '')}
			<div class="message message-system">
				<div class="message-content">
					<div class="system-indicator">
						<Icon icon="solar:info-circle-bold-duotone" width="16" />
						<span>시스템</span>
					</div>
					{#if parsed.vehicleData}
						<button class="vehicle-data-toggle" onclick={() => onToggleVehicleData(index)}>
							<Icon
								icon={collapsedVehicleData[index] === false
									? 'solar:alt-arrow-down-bold'
									: 'solar:alt-arrow-right-bold'}
								width="14"
							/>
							<span>Vehicle Data ({parsed.vehicleDataCount}개 항목)</span>
						</button>
						{#if collapsedVehicleData[index] === false}
							<pre class="vehicle-data-content">{parsed.vehicleData}</pre>
						{/if}
						<div class="markdown-content system-other-content">
							{@html marked(parsed.otherContent)}
						</div>
					{:else}
						<p>{message.content}</p>
					{/if}
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
						<div class="markdown-content">{@html marked(preprocessMarkdown(message.content || ''))}</div>
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

<style>
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
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
		flex-direction: row;
	}

	.message-wrapper-assistant {
		align-self: flex-start;
		flex-direction: row;
	}

	.message {
		display: flex;
	}

	.message-user {
		align-self: flex-end;
	}

	.message-user .message-content {
		background: var(--color-chat-user-bg);
		color: white;
		border-radius: 12px 12px 4px 12px;
	}

	.message-assistant {
		align-self: flex-start;
	}

	.message-assistant .message-content {
		background: var(--color-chat-assistant-bg);
		color: var(--color-chat-assistant-text);
		border-radius: 12px 12px 12px 4px;
	}

	.message-system {
		align-self: center;
		max-width: 90%;
	}

	.message-system .message-content {
		background: rgba(100, 116, 139, 0.1);
		color: var(--color-text-secondary);
		border-radius: 8px;
		border: 1px dashed rgba(100, 116, 139, 0.3);
		padding: 0.5rem 0.75rem;
		font-size: 0.85rem;
	}

	.system-indicator {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-weight: 600;
		font-size: 0.75rem;
		margin-bottom: 0.25rem;
		opacity: 0.8;
	}

	.vehicle-data-toggle {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		background: rgba(100, 116, 139, 0.15);
		border: none;
		border-radius: 4px;
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		color: var(--color-text-secondary);
		cursor: pointer;
		margin: 0.5rem 0;
		transition: background 0.2s;
	}

	.vehicle-data-toggle:hover {
		background: rgba(100, 116, 139, 0.25);
	}

	.vehicle-data-content {
		background: rgba(0, 0, 0, 0.05);
		border-radius: 4px;
		padding: 0.5rem;
		font-size: 0.7rem;
		line-height: 1.4;
		max-height: 200px;
		overflow-y: auto;
		margin: 0 0 0.5rem 0;
		font-family: 'Consolas', 'Monaco', monospace;
		white-space: pre-wrap;
		word-break: break-all;
	}

	.system-other-content {
		margin-top: 0.25rem;
	}

	.system-other-content :global(h1),
	.system-other-content :global(h2),
	.system-other-content :global(h3) {
		font-size: 0.85rem;
		font-weight: 600;
		margin: 0.5rem 0 0.25rem 0;
	}

	.system-other-content :global(p) {
		margin: 0.25rem 0;
	}

	.message-action {
		align-self: flex-start;
		max-width: 70%;
	}

	.message-action .message-content {
		background: var(--color-chat-action-bg);
		color: var(--color-chat-action-text);
		border-radius: 12px;
		border-left: 3px solid var(--color-chat-action-border);
		padding: 0.5rem 0.75rem;
	}

	.message-error .message-content {
		background: rgba(245, 101, 101, 0.2);
		color: var(--color-error);
		border-radius: 12px;
	}

	.action-indicator {
		font-weight: 600;
		font-size: 0.85rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.message-content {
		padding: 0.75rem 1rem;
		word-wrap: break-word;
		font-size: 0.9rem;
	}

	.message-content p {
		margin: 0;
		line-height: 1.5;
		white-space: pre-wrap;
	}

	.markdown-content {
		line-height: 1.6;
		font-size: 0.9rem;
	}

	.markdown-content :global(p) {
		margin: 0 0 0.5rem 0;
	}

	.markdown-content :global(p:last-child) {
		margin-bottom: 0;
	}

	.markdown-content :global(strong) {
		font-weight: 700;
		color: inherit;
	}

	.markdown-content :global(em) {
		font-style: italic;
	}

	.markdown-content :global(code) {
		background: var(--overlay-light);
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.9em;
	}

	.markdown-content :global(pre) {
		background: var(--overlay-light);
		padding: 0.75rem;
		border-radius: 6px;
		overflow-x: auto;
		overflow-y: visible;
		margin: 0.5rem 0;
		white-space: pre-wrap;
		word-break: break-word;
		max-height: none;
	}

	.markdown-content :global(pre code) {
		background: none;
		padding: 0;
		white-space: pre-wrap;
		word-break: break-word;
	}

	.markdown-content :global(ul),
	.markdown-content :global(ol) {
		margin: 0.5rem 0;
		padding-left: 1.5rem;
	}

	.markdown-content :global(li) {
		margin: 0.25rem 0;
	}

	.markdown-content :global(blockquote) {
		border-left: 3px solid var(--border-medium);
		padding-left: 0.75rem;
		margin: 0.5rem 0;
		font-style: italic;
		opacity: 0.9;
	}

	.markdown-content :global(h1),
	.markdown-content :global(h2),
	.markdown-content :global(h3),
	.markdown-content :global(h4),
	.markdown-content :global(h5),
	.markdown-content :global(h6) {
		margin: 0.75rem 0 0.5rem 0;
		font-weight: 700;
	}

	.markdown-content :global(h1) {
		font-size: 1.5em;
	}
	.markdown-content :global(h2) {
		font-size: 1.3em;
	}
	.markdown-content :global(h3) {
		font-size: 1.1em;
	}

	.markdown-content :global(a) {
		color: var(--color-chat-user-bg);
		text-decoration: underline;
	}

	.markdown-content :global(hr) {
		border: none;
		border-top: 1px solid var(--border-light);
		margin: 0.75rem 0;
	}

	.message-time {
		display: block;
		font-size: 0.7rem;
		color: var(--color-text-muted);
		white-space: nowrap;
		padding-bottom: 0.25rem;
	}

	.message-time-user {
		text-align: right;
	}

	.message-time-assistant {
		text-align: left;
	}

	.loading {
		display: flex;
		gap: 0.5rem;
	}

	.loading .dot {
		width: 8px;
		height: 8px;
		background: var(--color-text-muted);
		border-radius: 50%;
		animation: bounce 1.4s infinite ease-in-out both;
	}

	.loading .dot:nth-child(1) {
		animation-delay: -0.32s;
	}

	.loading .dot:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes bounce {
		0%,
		80%,
		100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}
</style>
