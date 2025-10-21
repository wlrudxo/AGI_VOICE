<script>
	import { page } from '$app/stores';
	import Icon from '@iconify/svelte';

	let { children } = $props();

	// 하위 메뉴
	const subMenus = [
		{ path: '/map-settings/generator', icon: 'solar:map-bold-duotone', label: 'Map 생성' },
		{ path: '/map-settings/library', icon: 'solar:folder-with-files-bold-duotone', label: 'Map 라이브러리' },
		{ path: '/map-settings/rag-test', icon: 'solar:magnifer-zoom-in-bold-duotone', label: 'RAG 테스트' }
	];

	const currentPath = $derived($page.url.pathname);
</script>

<div class="map-settings-layout">
	<!-- 하위 사이드바 -->
	<aside class="sub-sidebar">
		<div class="sub-sidebar-header">
			<Icon icon="solar:map-point-wave-bold-duotone" width="24" height="24" />
			<h2>Map 설정</h2>
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
	.map-settings-layout {
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
