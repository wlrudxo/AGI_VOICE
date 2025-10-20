<script>
	import { onMount } from 'svelte';

	onMount(() => {
		// Redirect to generator as default
		window.location.href = '/map-settings/generator';
	});
</script>

<div class="loading">
	<p>Map 설정으로 이동중...</p>
</div>

<style>
	.loading {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		color: var(--color-text-secondary);
	}
</style>
