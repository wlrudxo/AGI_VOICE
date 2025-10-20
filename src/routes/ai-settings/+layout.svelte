<script>
	import { page } from '$app/stores';
	import Icon from '@iconify/svelte';

	let { children } = $props();

	// 하위 메뉴
	const subMenus = [
		{ path: '/ai-settings/chat-settings', icon: 'solar:chat-round-dots-bold-duotone', label: '채팅 설정' },
		{ path: '/ai-settings/system-messages', icon: 'solar:document-text-bold-duotone', label: '시스템 메시지' },
		{ path: '/ai-settings/characters', icon: 'solar:user-bold-duotone', label: '캐릭터' },
		{ path: '/ai-settings/commands', icon: 'solar:code-bold-duotone', label: '명령어 템플릿' },
		{ path: '/ai-settings/user-info', icon: 'solar:users-group-rounded-bold-duotone', label: '유저 정보' },
		{ path: '/ai-settings/final-message', icon: 'solar:check-read-bold-duotone', label: '최종 메시지' }
	];

	const currentPath = $derived($page.url.pathname);
</script>

<div class="ai-settings-layout">
	<!-- 하위 사이드바 -->
	<aside class="sub-sidebar">
		<div class="sub-sidebar-header">
			<Icon icon="solar:settings-bold-duotone" width="24" height="24" />
			<h2>AI 설정</h2>
		</div>

		<nav class="sub-nav">
			{#each subMenus as menu}
				<a
					href={menu.path}
					class="sub-nav-item"
					class:active={currentPath === menu.path}
				>
					<Icon icon={menu.icon} width="20" height="20" />
					<span>{menu.label}</span>
				</a>
			{/each}
		</nav>
	</aside>

	<!-- 메인 컨텐츠 -->
	<main class="sub-content">
		{@render children?.()}
	</main>
</div>

<style>
	.ai-settings-layout {
		display: flex;
		height: 100%;
		background: var(--color-background);
	}

	.sub-sidebar {
		width: 16rem;
		border-right: 1px solid var(--color-border);
		display: flex;
		flex-direction: column;
		background-color: var(--color-surface);
	}

	.sub-sidebar-header {
		padding: 1.5rem;
		border-bottom: 1px solid var(--color-border);
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: var(--color-primary);
	}

	.sub-sidebar-header h2 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.sub-nav {
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.sub-nav-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		border-radius: 0.5rem;
		text-decoration: none;
		transition: all 0.2s;
		font-weight: 500;
		color: var(--color-text-secondary);
	}

	.sub-nav-item:hover {
		background-color: var(--color-surface-hover);
		color: var(--color-text-primary);
	}

	.sub-nav-item.active {
		background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
		color: white;
	}

	.sub-content {
		flex: 1;
		overflow-y: auto;
		padding: 2rem;
	}
</style>
