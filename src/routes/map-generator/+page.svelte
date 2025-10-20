<script>
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import Icon from '@iconify/svelte';
	import MapCanvas from '$lib/components/MapCanvas.svelte';

	// State
	let mapName = $state('');
	let mapDescription = $state('');
	let nodeXml = $state(`<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="center" x="0.0" y="0.0" type="traffic_light"/>
    <node id="north" x="0.0" y="100.0" type="priority"/>
    <node id="south" x="0.0" y="-100.0" type="priority"/>
    <node id="east" x="100.0" y="0.0" type="priority"/>
    <node id="west" x="-100.0" y="0.0" type="priority"/>
</nodes>`);

	let edgeXml = $state(`<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="north_to_center" from="north" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_north" from="center" to="north" priority="3" numLanes="2" speed="13.89"/>
    <edge id="south_to_center" from="south" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_south" from="center" to="south" priority="3" numLanes="2" speed="13.89"/>
    <edge id="east_to_center" from="east" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_east" from="center" to="east" priority="3" numLanes="2" speed="13.89"/>
    <edge id="west_to_center" from="west" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_west" from="center" to="west" priority="3" numLanes="2" speed="13.89"/>
</edges>`);

	let parsedNodes = $state([]);
	let parsedEdges = $state([]);
	let parseError = $state(null);
	let saveMessage = $state(null);

	// Parse XML
	function parseXml() {
		parseError = null;
		try {
			// Parse nodes
			const nodeParser = new DOMParser();
			const nodeDoc = nodeParser.parseFromString(nodeXml, 'text/xml');
			const nodeElements = nodeDoc.querySelectorAll('node');

			parsedNodes = Array.from(nodeElements).map(node => ({
				id: node.getAttribute('id'),
				x: parseFloat(node.getAttribute('x')),
				y: parseFloat(node.getAttribute('y')),
				type: node.getAttribute('type')
			}));

			// Parse edges
			const edgeParser = new DOMParser();
			const edgeDoc = edgeParser.parseFromString(edgeXml, 'text/xml');
			const edgeElements = edgeDoc.querySelectorAll('edge');

			parsedEdges = Array.from(edgeElements).map(edge => ({
				id: edge.getAttribute('id'),
				from: edge.getAttribute('from'),
				to: edge.getAttribute('to'),
				numLanes: parseInt(edge.getAttribute('numLanes') || '1'),
				speed: parseFloat(edge.getAttribute('speed') || '13.89')
			}));

			console.log('Parsed nodes:', $state.snapshot(parsedNodes));
			console.log('Parsed edges:', $state.snapshot(parsedEdges));
		} catch (error) {
			parseError = error.message;
			console.error('Parse error:', error);
		}
	}

	// Auto-parse on mount
	onMount(() => {
		parseXml();
	});

	// Save to DB
	async function saveToDb() {
		if (!mapName.trim()) {
			saveMessage = { type: 'error', text: '맵 이름을 입력해주세요.' };
			setTimeout(() => { saveMessage = null; }, 3000);
			return;
		}

		if (!mapDescription.trim()) {
			saveMessage = { type: 'error', text: '맵 설명을 입력해주세요.' };
			setTimeout(() => { saveMessage = null; }, 3000);
			return;
		}

		try {
			const map = await invoke('create_map', {
				request: {
					name: mapName.trim(),
					description: mapDescription.trim(),
					nodeXml: nodeXml,
					edgeXml: edgeXml,
					tags: null,
					category: 'general',
					difficulty: 'medium',
					metadata: null
				}
			});

			saveMessage = { type: 'success', text: `맵 "${map.name}"이 저장되었습니다. (ID: ${map.id})` };

			// Reset form
			mapName = '';
			mapDescription = '';

			setTimeout(() => { saveMessage = null; }, 5000);
		} catch (error) {
			console.error('Save error:', error);
			saveMessage = { type: 'error', text: `저장 실패: ${error}` };
			setTimeout(() => { saveMessage = null; }, 5000);
		}
	}
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>Map 생성</h1>
			<p class="subtitle">SUMO XML 노드와 엣지를 입력하여 맵을 생성하고 시각화합니다.</p>
		</div>
		<div class="header-actions">
			<button class="btn-secondary" onclick={parseXml}>
				<Icon icon="solar:refresh-bold" width="20" height="20" />
				미리보기
			</button>
			<button class="btn-primary" onclick={saveToDb}>
				<Icon icon="solar:diskette-bold" width="20" height="20" />
				DB 저장
			</button>
		</div>
	</div>

	{#if saveMessage}
		<div class="message-box {saveMessage.type}">
			<Icon icon="solar:info-circle-bold" width="20" height="20" />
			<span>{saveMessage.text}</span>
		</div>
	{/if}

	<div class="content-grid">
		<!-- Left Panel: XML Input -->
		<div class="input-panel">
			<div class="input-section">
				<label>
					<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
					맵 이름
				</label>
				<input
					type="text"
					bind:value={mapName}
					placeholder="예: crossroad_01"
					class="input-field"
				/>
			</div>

			<div class="input-section">
				<label>
					<Icon icon="solar:text-bold-duotone" width="20" height="20" />
					맵 설명
				</label>
				<textarea
					bind:value={mapDescription}
					placeholder="RAG 검색에 사용될 맵 설명을 입력하세요. 예: 신호등이 있는 4거리 교차로. 2차선 도로가 십자형으로 교차함."
					rows="3"
				></textarea>
			</div>

			<div class="input-section">
				<label>
					<Icon icon="solar:point-on-map-bold-duotone" width="20" height="20" />
					Node XML
				</label>
				<textarea
					bind:value={nodeXml}
					placeholder="노드 XML을 입력하세요..."
					rows="12"
				></textarea>
			</div>

			<div class="input-section">
				<label>
					<Icon icon="solar:route-bold-duotone" width="20" height="20" />
					Edge XML
				</label>
				<textarea
					bind:value={edgeXml}
					placeholder="엣지 XML을 입력하세요..."
					rows="12"
				></textarea>
			</div>

			{#if parseError}
				<div class="error-box">
					<Icon icon="solar:danger-triangle-bold" width="20" height="20" />
					<span>파싱 오류: {parseError}</span>
				</div>
			{/if}
		</div>

		<!-- Right Panel: Map Visualization -->
		<div class="preview-panel">
			<div class="preview-header">
				<Icon icon="solar:eye-bold-duotone" width="20" height="20" />
				<span>맵 미리보기</span>
			</div>
			<div class="canvas-wrapper">
				<MapCanvas nodes={parsedNodes} edges={parsedEdges} />
			</div>
			<div class="stats">
				<div class="stat-item">
					<Icon icon="solar:point-on-map-bold" width="16" height="16" />
					<span>노드: {parsedNodes.length}개</span>
				</div>
				<div class="stat-item">
					<Icon icon="solar:route-bold" width="16" height="16" />
					<span>엣지: {parsedEdges.length}개</span>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.page-container {
		max-width: 1400px;
		padding: 2rem;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 2rem;
	}

	.page-header h1 {
		margin: 0;
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-text-primary);
	}

	.subtitle {
		margin: 0.5rem 0 0 0;
		color: var(--color-text-secondary);
		font-size: 1rem;
	}

	.header-actions {
		display: flex;
		gap: 1rem;
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		height: calc(100vh - 200px);
	}

	.input-panel,
	.preview-panel {
		background: white;
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
		display: flex;
		flex-direction: column;
	}

	.input-section {
		margin-bottom: 1.5rem;
	}

	.input-section label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
		font-size: 0.95rem;
	}

	textarea {
		width: 100%;
		padding: 1rem;
		border: 1px solid var(--color-border-dark);
		border-radius: 0.5rem;
		font-size: 0.85rem;
		font-family: 'Consolas', 'Monaco', monospace;
		line-height: 1.6;
		resize: vertical;
		background: var(--color-background);
	}

	textarea:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.error-box {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: rgba(245, 101, 101, 0.1);
		border: 1px solid var(--color-error);
		border-radius: 0.5rem;
		color: var(--color-error);
		font-size: 0.875rem;
	}

	.message-box {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		margin-bottom: 1rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		animation: slideDown 0.3s ease-out;
	}

	.message-box.info {
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid #3b82f6;
		color: #1e40af;
	}

	.message-box.success {
		background: rgba(16, 185, 129, 0.1);
		border: 1px solid #10b981;
		color: #065f46;
	}

	.message-box.error {
		background: rgba(245, 101, 101, 0.1);
		border: 1px solid #ef4444;
		color: #991b1b;
	}

	.input-field {
		width: 100%;
		padding: 0.75rem 1rem;
		border: 1px solid var(--color-border-dark);
		border-radius: 0.5rem;
		font-size: 0.9rem;
		font-family: inherit;
	}

	.input-field:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.preview-panel {
		display: flex;
		flex-direction: column;
	}

	.preview-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1rem;
		font-weight: 600;
		color: var(--color-text-primary);
		font-size: 1rem;
	}

	.canvas-wrapper {
		flex: 1;
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		overflow: hidden;
		background: var(--color-background);
		min-height: 400px;
	}

	.stats {
		display: flex;
		gap: 1rem;
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid var(--color-border);
	}

	.stat-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: var(--color-text-secondary);
		font-size: 0.875rem;
	}
</style>
