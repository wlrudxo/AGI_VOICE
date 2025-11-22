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

	function toggleSubSidebar() {
		isCollapsed = !isCollapsed;
	}
</script>

<div class="sub-sidebar-layout" style={isCollapsed ? '--sub-sidebar-width: 5.5rem;' : ''}>
	<!-- 하위 사이드바 -->
	<aside class="sub-sidebar" class:collapsed={isCollapsed}>
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
			<button class="sub-sidebar-toggle-btn" on:click={toggleSubSidebar}>
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
