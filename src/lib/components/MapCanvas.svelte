<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';

	// Props
	let { nodes = [], edges = [] } = $props();

	// Canvas dimensions
	let canvasWidth = $state(800);
	let canvasHeight = $state(600);
	let scale = $state(1);
	let offsetX = $state(0);
	let offsetY = $state(0);

	// Calculate map bounds
	let mapBounds = $derived(calculateBounds(nodes));
	let viewBox = $derived(calculateViewBox(mapBounds, canvasWidth, canvasHeight));

	function calculateBounds(nodeList) {
		if (!nodeList || nodeList.length === 0) {
			return { minX: -100, maxX: 100, minY: -100, maxY: 100 };
		}

		let minX = Infinity, maxX = -Infinity;
		let minY = Infinity, maxY = -Infinity;

		nodeList.forEach(node => {
			minX = Math.min(minX, node.x);
			maxX = Math.max(maxX, node.x);
			minY = Math.min(minY, node.y);
			maxY = Math.max(maxY, node.y);
		});

		// Add padding
		const padding = 50;
		return {
			minX: minX - padding,
			maxX: maxX + padding,
			minY: minY - padding,
			maxY: maxY + padding
		};
	}

	function calculateViewBox(bounds, width, height) {
		const mapWidth = bounds.maxX - bounds.minX;
		const mapHeight = bounds.maxY - bounds.minY;

		// Calculate scale to fit
		const scaleX = width / mapWidth;
		const scaleY = height / mapHeight;
		const fitScale = Math.min(scaleX, scaleY) * 0.9;

		// Center the map
		const centerX = (bounds.minX + bounds.maxX) / 2;
		const centerY = (bounds.minY + bounds.maxY) / 2;

		return {
			x: centerX - width / (2 * fitScale),
			y: centerY - height / (2 * fitScale),
			width: width / fitScale,
			height: height / fitScale
		};
	}

	// Transform node coordinates to canvas coordinates
	function transformCoords(x, y) {
		return {
			x: x,
			y: -y // Flip Y-axis (SVG y goes down, map y goes up)
		};
	}

	// Get node by id
	function getNode(nodeId) {
		return nodes.find(n => n.id === nodeId);
	}

	// Get edge path
	function getEdgePath(edge) {
		const fromNode = getNode(edge.from);
		const toNode = getNode(edge.to);

		if (!fromNode || !toNode) return '';

		const from = transformCoords(fromNode.x, fromNode.y);
		const to = transformCoords(toNode.x, toNode.y);

		return `M ${from.x} ${from.y} L ${to.x} ${to.y}`;
	}

	// Get arrow position for edge
	function getArrowTransform(edge) {
		const fromNode = getNode(edge.from);
		const toNode = getNode(edge.to);

		if (!fromNode || !toNode) return '';

		const from = transformCoords(fromNode.x, fromNode.y);
		const to = transformCoords(toNode.x, toNode.y);

		// Calculate midpoint
		const midX = (from.x + to.x) / 2;
		const midY = (from.y + to.y) / 2;

		// Calculate angle
		const dx = to.x - from.x;
		const dy = to.y - from.y;
		const angle = Math.atan2(dy, dx) * 180 / Math.PI;

		return `translate(${midX}, ${midY}) rotate(${angle})`;
	}

	// Node colors by type
	function getNodeColor(type) {
		switch (type) {
			case 'traffic_light':
				return '#ef4444'; // red
			case 'priority':
				return '#3b82f6'; // blue
			case 'right_before_left':
				return '#10b981'; // green
			default:
				return '#6b7280'; // gray
		}
	}

	// Reset view
	function resetView() {
		scale = 1;
		offsetX = 0;
		offsetY = 0;
	}
</script>

<div class="map-canvas">
	{#if nodes.length === 0}
		<div class="empty-state">
			<Icon icon="solar:map-bold-duotone" width="64" height="64" />
			<p>노드 데이터가 없습니다</p>
			<p class="hint">XML을 입력하고 미리보기 버튼을 눌러주세요</p>
		</div>
	{:else}
		<svg
			width="100%"
			height="100%"
			viewBox="{viewBox.x} {viewBox.y} {viewBox.width} {viewBox.height}"
			preserveAspectRatio="xMidYMid meet"
		>
			<!-- Grid (optional) -->
			<defs>
				<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
					<path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" stroke-width="0.5"/>
				</pattern>
				<!-- Arrow marker -->
				<marker
					id="arrowhead"
					markerWidth="10"
					markerHeight="10"
					refX="5"
					refY="3"
					orient="auto"
					markerUnits="strokeWidth"
				>
					<path d="M0,0 L0,6 L9,3 z" fill="#64748b" />
				</marker>
			</defs>

			<!-- Background grid -->
			<rect
				x={viewBox.x}
				y={viewBox.y}
				width={viewBox.width}
				height={viewBox.height}
				fill="url(#grid)"
			/>

			<!-- Edges -->
			<g class="edges">
				{#each edges as edge}
					<path
						d={getEdgePath(edge)}
						stroke="#64748b"
						stroke-width="2"
						fill="none"
						marker-mid="url(#arrowhead)"
						opacity="0.6"
					/>
					<!-- Arrow at midpoint -->
					<g transform={getArrowTransform(edge)}>
						<circle r="3" fill="#64748b" />
					</g>
				{/each}
			</g>

			<!-- Nodes -->
			<g class="nodes">
				{#each nodes as node}
					{@const coords = transformCoords(node.x, node.y)}
					<g class="node">
						<!-- Node circle -->
						<circle
							cx={coords.x}
							cy={coords.y}
							r="8"
							fill={getNodeColor(node.type)}
							stroke="white"
							stroke-width="2"
						/>
						<!-- Node label -->
						<text
							x={coords.x}
							y={coords.y - 15}
							text-anchor="middle"
							font-size="10"
							font-weight="600"
							fill="#1f2937"
						>
							{node.id}
						</text>
						<!-- Node type label -->
						<text
							x={coords.x}
							y={coords.y + 20}
							text-anchor="middle"
							font-size="8"
							fill="#6b7280"
						>
							{node.type}
						</text>
					</g>
				{/each}
			</g>
		</svg>

		<!-- Controls -->
		<div class="controls">
			<button class="control-btn" onclick={resetView} title="화면 초기화">
				<Icon icon="solar:restart-bold" width="16" height="16" />
			</button>
		</div>
	{/if}
</div>

<style>
	.map-canvas {
		width: 100%;
		height: 100%;
		position: relative;
		background: var(--color-background);
		border-radius: 0.5rem;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--color-text-muted);
		gap: 0.5rem;
	}

	.empty-state p {
		margin: 0;
	}

	.hint {
		font-size: 0.875rem;
		opacity: 0.7;
	}

	svg {
		display: block;
	}

	.node {
		cursor: pointer;
		transition: transform 0.2s;
	}

	.node:hover {
		transform: scale(1.1);
	}

	.controls {
		position: absolute;
		bottom: 1rem;
		right: 1rem;
		display: flex;
		gap: 0.5rem;
	}

	.control-btn {
		padding: 0.5rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
		box-shadow: var(--shadow-sm);
		color: var(--color-text-secondary);
	}

	.control-btn:hover {
		background: var(--color-surface-hover);
		border-color: var(--color-primary);
		color: var(--color-primary);
	}
</style>
