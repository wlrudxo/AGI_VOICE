<script>
	import Icon from '@iconify/svelte';
	import { uiStore } from '$lib/stores/uiStore';

	async function minimizeWindow() {
		window.desktop?.window?.minimize?.();
	}

	async function maximizeWindow() {
		window.desktop?.window?.toggleMaximize?.();
	}

	async function closeWindow() {
		window.desktop?.window?.close?.();
	}

	function toggleWidgetMode() {
		uiStore.setWidgetMode(true);
	}
</script>

<div class="titlebar" style="-webkit-app-region: drag;">
	<div class="titlebar-left">
		<span class="app-title">AGI Voice</span>
	</div>

	<div class="titlebar-right">
		<button class="titlebar-button" onclick={toggleWidgetMode} title="위젯 모드">
			<Icon icon="solar:widget-5-bold-duotone" width="18" height="18" />
		</button>
		<button class="titlebar-button" onclick={minimizeWindow} title="최소화">
			<Icon icon="solar:minus-square-linear" width="18" height="18" />
		</button>
		<button class="titlebar-button" onclick={maximizeWindow} title="최대화">
			<Icon icon="solar:stop-bold-duotone" width="18" height="18" />
		</button>
		<button class="titlebar-button close" onclick={closeWindow} title="닫기">
			<Icon icon="solar:close-square-linear" width="18" height="18" />
		</button>
	</div>
</div>

<style>
	.titlebar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 40px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 12px;
		z-index: 9999;
		user-select: none;
		border-bottom: 1px solid var(--border-light);
	}
	.titlebar {
		background-color: var(--color-sidebar-bg);
	}

	.titlebar-left {
		display: flex;
		align-items: center;
		flex: 1;
	}

	.app-title {
		font-weight: 600;
		font-size: 14px;
		letter-spacing: 0.3px;
		color: var(--color-sidebar-text);
	}

	.titlebar-right {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.titlebar-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		background: transparent;
		border: none;
		cursor: pointer;
		border-radius: 6px;
		transition: all 0.2s;
		color: var(--color-sidebar-text);
	}

	.titlebar-button:hover {
		background-color: var(--color-sidebar-hover);
	}

	.titlebar-button:active {
		transform: scale(0.95);
		background-color: var(--color-sidebar-active);
	}

	.titlebar-button.close:hover {
		background: var(--color-close-hover);
		color: white;
	}

	.titlebar-button.close:active {
		background: var(--color-close-active);
	}
</style>
