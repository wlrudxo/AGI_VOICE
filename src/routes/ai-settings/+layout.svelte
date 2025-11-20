<script>
	import { page } from '$app/stores';
	import Icon from '@iconify/svelte';
	import Tooltip from '$lib/components/Tooltip.svelte';

	let { children } = $props();
	let isCollapsed = $state(false);

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
	const subSidebarWidth = $derived(isCollapsed ? '5.5rem' : '16rem');

	function toggleSubSidebar() {
		isCollapsed = !isCollapsed;
	}
</script>

<div class="ai-settings-layout">
	<!-- 하위 사이드바 -->
	<aside
		class="sub-sidebar"
		class:collapsed={isCollapsed}
		style={`--sub-sidebar-width: ${subSidebarWidth};`}
	>
		<div class="sub-sidebar-header" class:collapsed={isCollapsed}>
			<Icon icon="solar:settings-bold-duotone" width="24" height="24" />
			{#if !isCollapsed}
				<h2>AI 설정</h2>
			{/if}
		</div>

		<nav class="sub-nav">
			{#each subMenus as menu}
				{#if isCollapsed}
					<Tooltip text={menu.label} position="right">
						<a
							href={menu.path}
							class="sub-nav-item collapsed"
							class:active={currentPath === menu.path}
						>
							<Icon icon={menu.icon} width="20" height="20" />
						</a>
					</Tooltip>
				{:else}
					<a
						href={menu.path}
						class="sub-nav-item"
						class:active={currentPath === menu.path}
					>
						<Icon icon={menu.icon} width="20" height="20" />
						<span>{menu.label}</span>
					</a>
				{/if}
			{/each}
		</nav>

		<div class="sub-sidebar-footer">
			<button class="toggle-btn" on:click={toggleSubSidebar}>
				<Icon
					icon={isCollapsed ? 'solar:alt-arrow-right-bold-duotone' : 'solar:alt-arrow-left-bold-duotone'}
					width="24"
					height="24"
				/>
			</button>
		</div>
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
		width: var(--sub-sidebar-width, 16rem);
		border-right: 1px solid var(--color-border);
		display: flex;
		flex-direction: column;
		background-color: var(--color-surface);
		transition: width 200ms ease;
		overflow: hidden;
	}

	.sub-sidebar-header {
		padding: 1.5rem;
		border-bottom: 1px solid var(--color-border);
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: var(--color-primary);
	}

	.sub-sidebar-header.collapsed {
		justify-content: center;
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
		flex: 1;
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

	.sub-nav-item.collapsed {
		justify-content: center;
		width: 3.5rem;
		height: 3.5rem;
		margin: 0 auto;
	}

	.sub-nav-item.active {
		background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
		color: white;
	}

	.sub-sidebar-footer {
		padding: 1rem;
		border-top: 1px solid var(--color-border);
	}

	.sub-content {
		flex: 1;
		overflow-y: auto;
		padding: 2rem;
	}

	.toggle-btn {
		width: 3.5rem;
		height: 3.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 1px solid var(--border-light);
		border-radius: 0.5rem;
		background: var(--color-surface);
		color: var(--color-text-primary);
		cursor: pointer;
		transition: all 200ms;
	}

	.toggle-btn:hover {
		background-color: var(--color-surface-hover);
		border-color: var(--color-primary);
	}
</style>
