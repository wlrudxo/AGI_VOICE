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
	let editMapId = $state(null);
	let isEditMode = $state(false);
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

	// Auto-parse on mount
	onMount(() => {
		// Check for edit mode
		const urlParams = new URLSearchParams(window.location.search);
		const id = urlParams.get('id');

		if (id) {
			editMapId = parseInt(id);
			isEditMode = true;
			loadMapData(id);
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

	// Import sample maps to database
	async function importSampleMaps() {
		// Load existing maps to check for duplicates
		let existingMaps = [];
		try {
			existingMaps = await invoke('get_maps', { query: null });
		} catch (e) {
			console.error('❌ Failed to load existing maps:', e);
			saveMessage = { type: 'error', text: '기존 맵 로드 실패' };
			setTimeout(() => { saveMessage = null; }, 3000);
			return;
		}

		const existingNames = new Set(existingMaps.map(m => m.name));

		const sampleMaps = [
			{
				name: 'y_junction_01',
				description: 'Y자 모양의 삼거리 교차로입니다. 하단에서 올라오는 도로가 중앙 지점에서 두 갈래로 나뉘어 좌측 상단과 우측 상단으로 분기됩니다. 세 개의 방향으로 연결되며, 중앙 교차점을 중심으로 120도 간격으로 배치됩니다. 2차선 도로로 구성되며, 속도는 50km/h(13.89m/s)입니다. 분기 지점, 삼거리, Y자 교차로, 양갈래 도로에 적합합니다.',
				nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- Y형 교차로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <!-- 중앙 교차로 노드 -->
    <node id="center" x="0.0" y="0.0" type="priority"/>
    <!-- 하단 노드 (줄기) -->
    <node id="bottom" x="0.0" y="-100.0" type="priority"/>
    <!-- 좌측 상단 노드 -->
    <node id="top_left" x="-86.6" y="50.0" type="priority"/>
    <!-- 우측 상단 노드 -->
    <node id="top_right" x="86.6" y="50.0" type="priority"/>
</nodes>`,
				edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- Y형 교차로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="bottom_to_center" from="bottom" to="center" priority="2" numLanes="2" speed="13.89"/>
    <edge id="center_to_bottom" from="center" to="bottom" priority="2" numLanes="2" speed="13.89"/>
    <edge id="center_to_top_left" from="center" to="top_left" priority="2" numLanes="2" speed="13.89"/>
    <edge id="top_left_to_center" from="top_left" to="center" priority="2" numLanes="2" speed="13.89"/>
    <edge id="center_to_top_right" from="center" to="top_right" priority="2" numLanes="2" speed="13.89"/>
    <edge id="top_right_to_center" from="top_right" to="center" priority="2" numLanes="2" speed="13.89"/>
</edges>`,
				tags: ['Y자 교차로', '삼거리', '분기 지점', '양갈래 도로'],
				category: 'junction',
				difficulty: 'medium'
			},
			{
				name: 't_junction_01',
				description: 'T자 모양의 삼거리 교차로입니다. 좌우로 이어지는 주 도로에 하단에서 올라오는 도로가 수직으로 연결됩니다. 세 개의 방향으로 연결되며, 일반적인 T자형 골목길이나 지선 도로 연결에 사용됩니다. 2차선 도로로 구성되며, 속도는 50km/h(13.89m/s)입니다. T자 교차로, 삼거리, 직각 분기, 측면 진입로에 적합합니다.',
				nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- T형 교차로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="center" x="0.0" y="0.0" type="priority"/>
    <node id="left" x="-100.0" y="0.0" type="priority"/>
    <node id="right" x="100.0" y="0.0" type="priority"/>
    <node id="bottom" x="0.0" y="-100.0" type="priority"/>
</nodes>`,
				edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- T형 교차로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="left_to_center" from="left" to="center" priority="2" numLanes="2" speed="13.89"/>
    <edge id="center_to_left" from="center" to="left" priority="2" numLanes="2" speed="13.89"/>
    <edge id="center_to_right" from="center" to="right" priority="2" numLanes="2" speed="13.89"/>
    <edge id="right_to_center" from="right" to="center" priority="2" numLanes="2" speed="13.89"/>
    <edge id="bottom_to_center" from="bottom" to="center" priority="2" numLanes="2" speed="13.89"/>
    <edge id="center_to_bottom" from="center" to="bottom" priority="2" numLanes="2" speed="13.89"/>
</edges>`,
				tags: ['T자 교차로', '삼거리', '직각 분기', '측면 진입로'],
				category: 'junction',
				difficulty: 'medium'
			},
			{
				name: 'crossroad_01',
				description: '네 방향이 교차하는 십자형 교차로입니다. 북쪽, 남쪽, 동쪽, 서쪽 네 방향의 도로가 중앙에서 만납니다. 신호등(traffic_light)이 설치되어 교통을 제어합니다. 2차선 도로로 구성되며, 속도는 50km/h(13.89m/s)입니다. 우선순위가 높은(priority 3) 주요 교차로로, 사거리, 십자로, 네거리, 신호등 교차로에 적합합니다.',
				nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 십자형 교차로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <!-- 중앙 교차로 노드 -->
    <node id="center" x="0.0" y="0.0" type="traffic_light"/>
    <!-- 북쪽 노드 -->
    <node id="north" x="0.0" y="100.0" type="priority"/>
    <!-- 남쪽 노드 -->
    <node id="south" x="0.0" y="-100.0" type="priority"/>
    <!-- 동쪽 노드 -->
    <node id="east" x="100.0" y="0.0" type="priority"/>
    <!-- 서쪽 노드 -->
    <node id="west" x="-100.0" y="0.0" type="priority"/>
</nodes>`,
				edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 십자형 교차로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <!-- 북쪽에서 중앙으로 -->
    <edge id="north_to_center" from="north" to="center" priority="3" numLanes="2" speed="13.89"/>
    <!-- 중앙에서 북쪽으로 -->
    <edge id="center_to_north" from="center" to="north" priority="3" numLanes="2" speed="13.89"/>
    <!-- 남쪽에서 중앙으로 -->
    <edge id="south_to_center" from="south" to="center" priority="3" numLanes="2" speed="13.89"/>
    <!-- 중앙에서 남쪽으로 -->
    <edge id="center_to_south" from="center" to="south" priority="3" numLanes="2" speed="13.89"/>
    <!-- 동쪽에서 중앙으로 -->
    <edge id="east_to_center" from="east" to="center" priority="3" numLanes="2" speed="13.89"/>
    <!-- 중앙에서 동쪽으로 -->
    <edge id="center_to_east" from="center" to="east" priority="3" numLanes="2" speed="13.89"/>
    <!-- 서쪽에서 중앙으로 -->
    <edge id="west_to_center" from="west" to="center" priority="3" numLanes="2" speed="13.89"/>
    <!-- 중앙에서 서쪽으로 -->
    <edge id="center_to_west" from="center" to="west" priority="3" numLanes="2" speed="13.89"/>
</edges>`,
				tags: ['사거리', '십자로', '네거리', '신호등 교차로'],
				category: 'junction',
				difficulty: 'medium'
			},
			{
				name: 'three_lane_road_01',
				description: '넓은 3차선 직선 도로입니다. 200m 길이의 일직선 도로로 양방향 모두 3차선입니다. 속도는 80km/h(22.22m/s)로 고속 주행이 가능합니다. 교통량이 많은 주요 간선도로나 고속화도로에 적합합니다. 대로, 넓은 도로, 간선도로, 주요 도로, 고속 도로, 다차선 도로에 사용됩니다.',
				nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 3차선 직선 도로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="start" x="0.0" y="0.0" type="priority"/>
    <node id="end" x="200.0" y="0.0" type="priority"/>
</nodes>`,
				edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 3차선 직선 도로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="start_to_end" from="start" to="end" priority="3" numLanes="3" speed="22.22"/>
    <edge id="end_to_start" from="end" to="start" priority="3" numLanes="3" speed="22.22"/>
</edges>`,
				tags: ['3차선', '넓은 도로', '간선도로', '주요 도로', '고속 도로', '다차선 도로'],
				category: 'highway',
				difficulty: 'easy'
			},
			{
				name: 'merge_lane_01',
				description: '진입 램프가 주 도로와 합류하는 구조입니다. 2차선 주 도로에 1차선 진입 램프가 비스듬히 연결되어 병합 지점에서 3차선으로 확장됩니다. 램프 속도는 60km/h(16.67m/s), 주 도로는 80km/h(22.22m/s)입니다. 고속도로 진입로, 합류 구간, 램프 연결, 차선 병합, 진입로 합류에 적합합니다.',
				nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 병합 차선을 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <!-- 주 도로 시작 노드 -->
    <node id="main_start" x="0.0" y="0.0" type="priority"/>
    <!-- 병합 지점 노드 -->
    <node id="merge_point" x="100.0" y="0.0" type="priority"/>
    <!-- 진입 램프 시작 노드 -->
    <node id="ramp_start" x="80.0" y="-50.0" type="priority"/>
    <!-- 종료 노드 -->
    <node id="end" x="200.0" y="0.0" type="priority"/>
</nodes>`,
				edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 병합 차선을 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <!-- 주 도로: 시작에서 병합 지점으로 -->
    <edge id="main_to_merge" from="main_start" to="merge_point" priority="3" numLanes="2" speed="22.22"/>
    <!-- 진입 램프: 램프 시작에서 병합 지점으로 -->
    <edge id="ramp_to_merge" from="ramp_start" to="merge_point" priority="2" numLanes="1" speed="16.67"/>
    <!-- 병합 후: 병합 지점에서 종료로 -->
    <edge id="merge_to_end" from="merge_point" to="end" priority="3" numLanes="3" speed="22.22"/>
    <!-- 역방향: 종료에서 병합 지점으로 -->
    <edge id="end_to_merge" from="end" to="merge_point" priority="3" numLanes="2" speed="22.22"/>
    <!-- 역방향: 병합 지점에서 시작으로 -->
    <edge id="merge_to_main" from="merge_point" to="main_start" priority="3" numLanes="2" speed="22.22"/>
</edges>`,
				tags: ['병합 차선', '진입 램프', '합류 구간', '차선 병합', '고속도로 진입로'],
				category: 'highway',
				difficulty: 'hard'
			},
			{
				name: 'straight_road_01',
				description: '단순한 직선 도로입니다. 300m 길이의 긴 일직선 도로로 양방향 2차선입니다. 속도는 50km/h(13.89m/s)입니다. 가장 기본적인 도로 형태로, 직선 구간, 단순 도로, 일반 도로, 기본 간선에 사용됩니다.',
				nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 1자형 직선 도로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="start" x="0.0" y="0.0" type="priority"/>
    <node id="end" x="300.0" y="0.0" type="priority"/>
</nodes>`,
				edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 1자형 직선 도로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="start_to_end" from="start" to="end" priority="2" numLanes="2" speed="13.89"/>
    <edge id="end_to_start" from="end" to="start" priority="2" numLanes="2" speed="13.89"/>
</edges>`,
				tags: ['1자형', '직선 도로', '단순 도로', '일반 도로', '기본 간선'],
				category: 'general',
				difficulty: 'easy'
			}
		];

		saveMessage = { type: 'info', text: '🚀 샘플 맵 Import 시작...' };
		let successCount = 0;
		let errorCount = 0;
		let skippedCount = 0;

		for (const map of sampleMaps) {
			// Skip if map name already exists
			if (existingNames.has(map.name)) {
				console.log(`⏭️ ${map.name} - 이미 존재하는 맵 (건너뜀)`);
				skippedCount++;
				continue;
			}

			try {
				await invoke('create_map', {
					request: {
						name: map.name,
						description: map.description,
						nodeXml: map.nodeXml,
						edgeXml: map.edgeXml,
						tags: map.tags,
						category: map.category,
						difficulty: map.difficulty,
						metadata: null
					}
				});
				console.log(`✅ ${map.name} 저장 완료`);
				successCount++;
			} catch (error) {
				console.error(`❌ ${map.name} 저장 실패:`, error);
				errorCount++;
			}
		}

		// Build result message
		let resultMessage = '';
		if (errorCount === 0 && skippedCount === 0) {
			resultMessage = `🎉 샘플 맵 ${successCount}개 Import 완료!`;
			saveMessage = { type: 'success', text: resultMessage };
		} else if (errorCount === 0) {
			resultMessage = `✅ ${successCount}개 생성, ${skippedCount}개 건너뜀 (중복)`;
			saveMessage = { type: 'success', text: resultMessage };
		} else {
			resultMessage = `⚠️ ${successCount}개 성공, ${errorCount}개 실패, ${skippedCount}개 건너뜀`;
			saveMessage = { type: 'error', text: resultMessage };
		}

		setTimeout(() => { saveMessage = null; }, 5000);
	}
</script>

<Dialog bind:this={dialog} />

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>{isEditMode ? 'Map 수정' : 'Map 생성'}</h1>
			<p class="subtitle">
				{isEditMode
					? 'SUMO XML 노드와 엣지를 수정하고 저장합니다.'
					: 'SUMO XML 노드와 엣지를 입력하여 맵을 생성하고 시각화합니다.'}
			</p>
		</div>
		<div class="header-actions">
			{#if !isEditMode}
				<button class="btn-secondary" onclick={importSampleMaps}>
					<Icon icon="solar:database-bold" width="20" height="20" />
					샘플 맵 Import
				</button>
			{/if}
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
					<Icon icon="solar:tag-bold-duotone" width="20" height="20" />
					태그
				</label>
				<input
					type="text"
					bind:value={mapTags}
					placeholder="쉼표로 구분하여 입력하세요. 예: 교차로, 신호등, 4거리"
					class="input-field"
				/>
				<small class="helper-text">태그는 쉼표(,)로 구분하여 입력하세요.</small>
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

	.helper-text {
		display: block;
		margin-top: 0.25rem;
		color: var(--color-text-secondary);
		font-size: 0.75rem;
	}
</style>
