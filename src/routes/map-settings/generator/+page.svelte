<script>
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import { readTextFile } from '@tauri-apps/plugin-fs';
	import { open } from '@tauri-apps/plugin-dialog';
	import { page } from '$app/stores';
	import Icon from '@iconify/svelte';
	import MapCanvas from '$lib/components/MapCanvas.svelte';
	import Dialog from '$lib/components/Dialog.svelte';

	// Dialog reference
	let dialog;

	// State
	let mapName = $state('');
	let mapDescription = $state('');
	let mapTags = $state('');
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

	// Load map data for edit mode
	async function loadMapData(id) {
		try {
			const map = await invoke('get_map_by_id', { id: parseInt(id) });

			// Populate fields
			mapName = map.name;
			mapDescription = map.description;
			nodeXml = map.nodeXml;
			edgeXml = map.edgeXml;

			// Handle tags (can be array, string, or null)
			if (map.tags) {
				if (Array.isArray(map.tags)) {
					mapTags = map.tags.join(', ');
				} else if (typeof map.tags === 'string') {
					// Try to parse JSON string
					try {
						const parsed = JSON.parse(map.tags);
						mapTags = Array.isArray(parsed) ? parsed.join(', ') : map.tags;
					} catch {
						// If not valid JSON, use as-is
						mapTags = map.tags;
					}
				} else {
					mapTags = '';
				}
			} else {
				mapTags = '';
			}

			// Parse and display
			parseXml();

			console.log('✅ Loaded map for editing:', map.name);
		} catch (error) {
			console.error('❌ Failed to load map:', error);
			saveMessage = { type: 'error', text: `맵 로드 실패: ${error}` };
			setTimeout(() => { saveMessage = null; }, 3000);
		}
	}

	// Reactive URL param (read-only)
	const editMapId = $derived.by(() => {
		const urlId = $page.url.searchParams.get('id');
		return urlId ? parseInt(urlId) : null;
	});
	const isEditMode = $derived(editMapId !== null);

	// Load map data on mount
	onMount(() => {
		if (editMapId) {
			loadMapData(editMapId);
		} else {
			parseXml();
		}
	});

	// Save to DB (create)
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

		// Convert comma-separated tags to array
		const tagsArray = mapTags.trim()
			? mapTags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
			: null;

		try {
			const map = await invoke('create_map', {
				request: {
					name: mapName.trim(),
					description: mapDescription.trim(),
					nodeXml: nodeXml,
					edgeXml: edgeXml,
					tags: tagsArray,
					category: 'general',
					difficulty: 'medium',
					metadata: null
				}
			});

			saveMessage = { type: 'success', text: `맵 "${map.name}"이 저장되었습니다. (ID: ${map.id})` };

			// Reset form
			mapName = '';
			mapDescription = '';
			mapTags = '';

			setTimeout(() => { saveMessage = null; }, 5000);
		} catch (error) {
			console.error('Save error:', error);
			saveMessage = { type: 'error', text: `저장 실패: ${error}` };
			setTimeout(() => { saveMessage = null; }, 5000);
		}
	}

	// Update map (edit mode)
	async function updateMap() {
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

		// Convert comma-separated tags to array
		const tagsArray = mapTags.trim()
			? mapTags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
			: null;

		try {
			const map = await invoke('update_map', {
				id: editMapId,
				request: {
					name: mapName.trim(),
					description: mapDescription.trim(),
					nodeXml: nodeXml,
					edgeXml: edgeXml,
					tags: tagsArray,
					category: null,
					difficulty: null,
					metadata: null
				}
			});

			saveMessage = { type: 'success', text: `맵 "${map.name}"이 수정되었습니다.` };
			setTimeout(() => {
				saveMessage = null;
				// Navigate back to library
				window.location.href = '/map-settings/library';
			}, 2000);
		} catch (error) {
			console.error('Update error:', error);
			saveMessage = { type: 'error', text: `수정 실패: ${error}` };
			setTimeout(() => { saveMessage = null; }, 5000);
		}
	}

	// Delete map (edit mode)
	async function deleteMap() {
		const confirmed = await dialog.confirm(
			`"${mapName}" 맵을 삭제하시겠습니까?`,
			'맵 삭제'
		);

		if (!confirmed) {
			return;
		}

		try {
			await invoke('delete_map', { id: editMapId });

			saveMessage = { type: 'success', text: '맵이 삭제되었습니다.' };
			setTimeout(() => {
				saveMessage = null;
				// Navigate back to library
				window.location.href = '/map-settings/library';
			}, 1500);
		} catch (error) {
			console.error('Delete error:', error);
			saveMessage = { type: 'error', text: `삭제 실패: ${error}` };
			setTimeout(() => { saveMessage = null; }, 5000);
		}
	}

	// Import XML files
	async function importXmlFiles() {
		try {
			const selected = await open({
				multiple: true,
				filters: [{
					name: 'SUMO XML Files',
					extensions: ['xml']
				}]
			});

			if (!selected || selected.length === 0) {
				return;
			}

			// Separate .edg.xml and .nod.xml files
			const edgFiles = selected.filter(path => path.endsWith('.edg.xml'));
			const nodFiles = selected.filter(path => path.endsWith('.nod.xml'));

			// Validation: Only 1 of each type allowed
			if (edgFiles.length > 1) {
				saveMessage = { type: 'error', text: '⚠️ .edg.xml 파일은 1개만 선택할 수 있습니다.' };
				setTimeout(() => { saveMessage = null; }, 3000);
				return;
			}

			if (nodFiles.length > 1) {
				saveMessage = { type: 'error', text: '⚠️ .nod.xml 파일은 1개만 선택할 수 있습니다.' };
				setTimeout(() => { saveMessage = null; }, 3000);
				return;
			}

			// Read and populate textareas
			if (nodFiles.length === 1) {
				const content = await readTextFile(nodFiles[0]);
				nodeXml = content;
				console.log('✅ Loaded node XML from:', nodFiles[0]);
			}

			if (edgFiles.length === 1) {
				const content = await readTextFile(edgFiles[0]);
				edgeXml = content;
				console.log('✅ Loaded edge XML from:', edgFiles[0]);
			}

			// Auto-parse after import
			parseXml();

			// Success message
			const importedTypes = [];
			if (nodFiles.length > 0) importedTypes.push('노드');
			if (edgFiles.length > 0) importedTypes.push('엣지');

			if (importedTypes.length > 0) {
				saveMessage = { type: 'success', text: `✅ ${importedTypes.join(', ')} XML을 불러왔습니다.` };
				setTimeout(() => { saveMessage = null; }, 3000);
			}
		} catch (error) {
			console.error('Import error:', error);
			saveMessage = { type: 'error', text: `파일 불러오기 실패: ${error}` };
			setTimeout(() => { saveMessage = null; }, 3000);
		}
	}

</script>

<Dialog bind:this={dialog} />

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>{isEditMode ? 'Map 수정' : 'Map 생성'}</h1>
			<p class="page-description">
				{isEditMode
					? 'SUMO XML 노드와 엣지를 수정하고 저장합니다.'
					: 'SUMO XML 노드와 엣지를 입력하여 맵을 생성하고 시각화합니다.'}
			</p>
		</div>
		<div class="header-actions">
			<button class="btn-secondary" onclick={importXmlFiles}>
				<Icon icon="solar:import-bold" width="20" height="20" />
				Import
			</button>
			<button class="btn-secondary" onclick={parseXml}>
				<Icon icon="solar:refresh-bold" width="20" height="20" />
				미리보기
			</button>
			{#if isEditMode}
				<button class="btn-danger" onclick={deleteMap}>
					<Icon icon="solar:trash-bin-trash-bold" width="20" height="20" />
					삭제
				</button>
				<button class="btn-primary" onclick={updateMap}>
					<Icon icon="solar:diskette-bold" width="20" height="20" />
					저장
				</button>
			{:else}
				<button class="btn-primary" onclick={saveToDb}>
					<Icon icon="solar:diskette-bold" width="20" height="20" />
					DB 저장
				</button>
			{/if}
		</div>
	</div>

	{#if saveMessage}
		<div class:alert-success={saveMessage.type === 'success'} class:alert-error={saveMessage.type === 'error'} class:alert-info={saveMessage.type === 'info'}>
			<Icon icon="solar:info-circle-bold" width="20" height="20" />
			<span>{saveMessage.text}</span>
		</div>
	{/if}

	<div class="content-grid">
		<!-- Left Panel: XML Input -->
		<div class="input-panel">
			<div class="form-group">
				<label class="form-label">
					<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
					맵 이름
				</label>
				<input
					type="text"
					bind:value={mapName}
					placeholder="예: crossroad_01"
					class="input-field w-full"
				/>
			</div>

			<div class="form-group">
				<label class="form-label">
					<Icon icon="solar:text-bold-duotone" width="20" height="20" />
					맵 설명
				</label>
				<textarea
					bind:value={mapDescription}
					placeholder="RAG 검색에 사용될 맵 설명을 입력하세요. 예: 신호등이 있는 4거리 교차로. 2차선 도로가 십자형으로 교차함."
					rows="3"
					class="textarea-field w-full"
				></textarea>
			</div>

			<div class="form-group">
				<label class="form-label">
					<Icon icon="solar:tag-bold-duotone" width="20" height="20" />
					태그
				</label>
				<input
					type="text"
					bind:value={mapTags}
					placeholder="쉼표로 구분하여 입력하세요. 예: 교차로, 신호등, 4거리"
					class="input-field w-full"
				/>
				<p class="form-hint">태그는 쉼표(,)로 구분하여 입력하세요.</p>
			</div>

			<div class="form-group">
				<label class="form-label">
					<Icon icon="solar:point-on-map-bold-duotone" width="20" height="20" />
					Node XML
				</label>
				<textarea
					bind:value={nodeXml}
					placeholder="노드 XML을 입력하세요..."
					rows="12"
					class="textarea-field w-full"
				></textarea>
			</div>

			<div class="form-group">
				<label class="form-label">
					<Icon icon="solar:route-bold-duotone" width="20" height="20" />
					Edge XML
				</label>
				<textarea
					bind:value={edgeXml}
					placeholder="엣지 XML을 입력하세요..."
					rows="12"
					class="textarea-field w-full"
				></textarea>
			</div>

			{#if parseError}
				<div class="alert-error">
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
		margin: 0 auto;
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		height: calc(100vh - 200px);
	}

	.input-panel,
	.preview-panel {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
		display: flex;
		flex-direction: column;
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
