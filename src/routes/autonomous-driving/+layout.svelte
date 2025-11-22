<script>
	import { page } from '$app/stores';
	import Icon from '@iconify/svelte';
	import Tooltip from '$lib/components/Tooltip.svelte';

	let { children } = $props();
	let isCollapsed = $state(false);

	// 하위 메뉴
	const subMenus = [
		{ path: '/autonomous-driving/vehicle-control', icon: 'solar:widget-2-bold-duotone', label: '차량 제어' },
		{ path: '/autonomous-driving/stop-conditions', icon: 'solar:atom-bold-duotone', label: '트리거 설정' },
		{ path: '/autonomous-driving/manual-control', icon: 'solar:gameboy-bold-duotone', label: '수동제어' },
		{ path: '/autonomous-driving/settings', icon: 'solar:settings-bold-duotone', label: '설정' }
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
			<Icon icon="solar:wheel-bold-duotone" width="24" height="24" />
			{#if !isCollapsed}
				<h2>자율주행</h2>
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
