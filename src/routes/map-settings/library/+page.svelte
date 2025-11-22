<script>
	import { onMount, onDestroy } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import Icon from '@iconify/svelte';
	import MapCard from '$lib/components/MapCard.svelte';
	import Dialog from '$lib/components/Dialog.svelte';
	import { dbWatcher } from '$lib/stores/dbWatcher.svelte';

	// Dialog reference
	let dialog;

	// State
	let maps = $state([]);
	let loading = $state(true);
	let error = $state(null);

	// Filter state
	let categoryFilter = $state('all');
	let embeddedFilter = $state('all');
	let searchQuery = $state('');

	// Filtered maps
	let filteredMaps = $derived.by(() => {
		let result = maps;

		// Category filter
		if (categoryFilter !== 'all') {
			result = result.filter(m => m.category === categoryFilter);
		}

		// Embedded filter
		if (embeddedFilter !== 'all') {
			const isEmbedded = embeddedFilter === 'embedded';
			result = result.filter(m => m.isEmbedded === (isEmbedded ? 1 : 0));
		}

		// Search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			result = result.filter(m =>
				m.name.toLowerCase().includes(query) ||
				m.description.toLowerCase().includes(query)
			);
		}

		return result;
	});

	// Load maps from database
	async function loadMaps() {
		try {
			loading = true;
			error = null;

			const response = await invoke('get_maps', {
				query: null
			});

			maps = response;
			console.log('✅ Loaded maps:', maps.length);
		} catch (e) {
			console.error('❌ Failed to load maps:', e);
			error = e;
		} finally {
			loading = false;
		}
	}

	// Handle map selection
	function handleSelectMap(map) {
		console.log('Map selected:', map.id);
		// TODO: Navigate to map detail page or open edit modal
	}

	// Handle map edit
	function handleEditMap(map) {
		// Navigate to map-generator with map id
		window.location.href = `/map-settings/generator?id=${map.id}`;
	}

	// Handle map deletion
	async function handleDeleteMap(map) {
		const confirmed = await dialog.confirm(
			`"${map.name}" 맵을 삭제하시겠습니까?`,
			'맵 삭제'
		);

		if (!confirmed) {
			return;
		}

		try {
			await invoke('delete_map', { id: map.id });
			console.log('✅ Map deleted:', map.id);
			await loadMaps(); // Reload after deletion
		} catch (e) {
			console.error('❌ Failed to delete map:', e);
			await dialog.alert(`맵 삭제 실패: ${e}`, '오류');
		}
	}

	// Handle single map embedding
	async function handleEmbedMap(map) {
		const confirmed = await dialog.confirm(
			`"${map.name}" 맵의 임베딩을 생성하시겠습니까?`,
			'임베딩 생성'
		);

		if (!confirmed) {
			return;
		}

		try {
			console.log('🔄 Embedding map:', map.id);
			const result = await invoke('embed_map', { mapId: map.id });

			if (result.success) {
				console.log('✅ Map embedded successfully:', result);
				await dialog.alert(`임베딩 생성 완료: ${map.name}`, '완료');
				await loadMaps(); // Reload to update embedded status
			} else {
				throw new Error(result.error || 'Unknown error');
			}
		} catch (e) {
			console.error('❌ Failed to embed map:', e);
			await dialog.alert(`임베딩 생성 실패: ${e}`, '오류');
		}
	}

	// Create sample maps
	async function createSampleMaps() {
		// Load existing maps to check for duplicates
		let existingMaps = [];
		try {
			existingMaps = await invoke('get_maps', { query: null });
		} catch (e) {
			console.error('❌ Failed to load existing maps:', e);
			await dialog.alert('기존 맵 로드 실패', '오류');
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
			resultMessage = `샘플 맵 ${successCount}개가 생성되었습니다.`;
		} else if (errorCount === 0) {
			resultMessage = `${successCount}개 생성, ${skippedCount}개 건너뜀 (중복)`;
		} else {
			resultMessage = `${successCount}개 성공, ${errorCount}개 실패, ${skippedCount}개 건너뜀`;
		}

		await dialog.alert(resultMessage, '샘플맵 생성 완료');
		await loadMaps(); // Reload maps
	}

	// Handle batch embedding (all maps)
	let buildingEmbeddings = $state(false);
	async function handleBuildAllEmbeddings() {
		const confirmed = await dialog.confirm(
			'모든 맵의 임베딩을 생성하시겠습니까?\n(시간이 걸릴 수 있습니다)',
			'전체 임베딩 생성'
		);

		if (!confirmed) {
			return;
		}

		try {
			buildingEmbeddings = true;
			console.log('🏗️ Building all embeddings...');

			const result = await invoke('build_all_embeddings', { rebuild: false });

			if (result.success) {
				console.log('✅ All embeddings built successfully:', result);
				await dialog.alert(
					`전체 임베딩 생성 완료!\n- 총 맵: ${result.totalMaps}개\n- 임베딩 완료: ${result.embeddedCount}개`,
					'완료'
				);
				await loadMaps(); // Reload to update embedded statuses
			} else {
				throw new Error(result.error || 'Unknown error');
			}
		} catch (e) {
			console.error('❌ Failed to build embeddings:', e);
			await dialog.alert(`전체 임베딩 생성 실패: ${e}`, '오류');
		} finally {
			buildingEmbeddings = false;
		}
	}

	// Get unique categories
	let categories = $derived.by(() => {
		const cats = new Set(maps.map(m => m.category));
		return Array.from(cats).sort();
	});

	// Auto-refresh setup
	let unsubscribe = null;

	onMount(() => {
		loadMaps();
		dbWatcher.startWatching();
		unsubscribe = dbWatcher.onChange(() => {
			console.log('🔄 DB changed, reloading maps...');
			loadMaps();
		});
	});

	onDestroy(() => {
		if (unsubscribe) unsubscribe();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>Map 라이브러리</h1>
			<p class="page-description">저장된 SUMO 맵을 조회하고 관리합니다.</p>
		</div>
		<div class="header-actions">
			<button class="btn-secondary" onclick={createSampleMaps}>
				<Icon icon="solar:map-point-bold" width="20" height="20" />
				샘플맵 생성
			</button>
			<button
				class="btn-secondary"
				onclick={handleBuildAllEmbeddings}
				disabled={buildingEmbeddings}
			>
				<Icon icon="solar:database-bold" width="20" height="20" />
				{buildingEmbeddings ? '임베딩 생성 중...' : '전체 맵 Embed'}
			</button>
			<a href="/map-settings/generator" class="btn-primary">
				<Icon icon="solar:add-circle-bold" width="20" height="20" />
				새 맵 생성
			</a>
		</div>
	</div>

	<!-- Filters -->
	<div class="filters-section">
		<div class="filter-group">
			<Icon icon="solar:magnifer-bold-duotone" width="20" height="20" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="맵 이름 또는 설명 검색..."
				class="search-input"
			/>
		</div>

		<div class="filter-group">
			<Icon icon="solar:widget-5-bold" width="20" height="20" />
			<select bind:value={categoryFilter} class="filter-select">
				<option value="all">모든 카테고리</option>
				{#each categories as category}
					<option value={category}>{category}</option>
				{/each}
			</select>
		</div>

		<div class="filter-group">
			<Icon icon="solar:database-bold-duotone" width="20" height="20" />
			<select bind:value={embeddedFilter} class="filter-select">
				<option value="all">모든 상태</option>
				<option value="embedded">임베딩 완료</option>
				<option value="not_embedded">임베딩 대기</option>
			</select>
		</div>

		<div class="stats-badge">
			<Icon icon="solar:map-point-bold" width="16" height="16" />
			<span>{filteredMaps.length}개 맵</span>
		</div>
	</div>

	<!-- Content -->
	<div class="content-section">
		{#if loading}
			<div class="loading-state">
				<Icon icon="solar:refresh-bold" width="48" height="48" class="spin" />
				<p>맵 로딩 중...</p>
			</div>
		{:else if error}
			<div class="error-state">
				<Icon icon="solar:danger-triangle-bold" width="48" height="48" />
				<p>맵 로딩 실패: {error}</p>
				<button class="btn-secondary" onclick={loadMaps}>
					<Icon icon="solar:refresh-bold" width="20" height="20" />
					다시 시도
				</button>
			</div>
		{:else if filteredMaps.length === 0}
			<div class="empty-state">
				<Icon icon="solar:map-point-bold-duotone" width="64" height="64" />
				<h3>맵이 없습니다</h3>
				<p>
					{searchQuery || categoryFilter !== 'all' || embeddedFilter !== 'all'
						? '검색 조건에 맞는 맵이 없습니다.'
						: '첫 번째 맵을 생성해보세요!'}
				</p>
				<a href="/map-settings/generator" class="btn-primary">
					<Icon icon="solar:add-circle-bold" width="20" height="20" />
					맵 생성하기
				</a>
			</div>
		{:else}
			<div class="maps-grid">
				{#each filteredMaps as map (map.id)}
					<MapCard
						{map}
						onSelect={handleSelectMap}
						onEdit={handleEditMap}
						onDelete={handleDeleteMap}
						onEmbed={handleEmbedMap}
					/>
				{/each}
			</div>
		{/if}
	</div>
</div>

<Dialog bind:this={dialog} />

<style>
	.page-container {
		max-width: 1400px;
		margin: 0 auto;
	}

	.filters-section {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
		flex-wrap: wrap;
		align-items: center;
		background: var(--color-surface);
		padding: 1.25rem;
		border-radius: 0.75rem;
		box-shadow: var(--shadow-sm);
	}

	.filter-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: var(--color-text-secondary);
	}

	.search-input {
		padding: 0.625rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		font-size: 0.9rem;
		min-width: 300px;
		background: var(--color-surface);
		color: var(--color-text-primary);
	}

	.search-input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.filter-select {
		padding: 0.625rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		font-size: 0.9rem;
		background: var(--color-surface);
		color: var(--color-text-primary);
		cursor: pointer;
	}

	.filter-select:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.stats-badge {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.875rem;
		background: var(--color-primary-bg-light);
		color: var(--color-primary);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		margin-left: auto;
	}

	.content-section {
		min-height: 400px;
	}

	.maps-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 1.5rem;
	}

	/* Loading state */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--color-text-secondary);
	}

	.loading-state :global(.spin) {
		animation: spin 1s linear infinite;
		color: var(--color-primary);
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.loading-state p {
		margin-top: 1rem;
		font-size: 1rem;
	}

	/* Error state */
	.error-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--color-error);
	}

	.error-state p {
		margin: 1rem 0;
		font-size: 1rem;
	}

	/* Empty state */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--color-text-secondary);
	}

	.empty-state h3 {
		margin: 1rem 0 0.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.empty-state p {
		margin-bottom: 1.5rem;
		font-size: 1rem;
	}

	.empty-state :global(svg) {
		color: var(--color-text-muted);
	}
</style>
