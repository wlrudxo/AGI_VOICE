<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		// Redirect to generator as default
		goto('/map-settings/generator');
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
