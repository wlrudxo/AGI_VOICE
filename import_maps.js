// Map 데이터 자동 Import 스크립트
// 사용법: Tauri 앱 실행 후 브라우저 DevTools 콘솔에서 이 스크립트를 복사/붙여넣기하여 실행

const { invoke } = window.__TAURI__.core;

const maps = [
  {
    name: 'y_junction_01',
    description: 'Y자 모양의 삼거리 교차로입니다. 하단에서 올라오는 도로가 중앙 지점에서 두 갈래로 나뉘어 좌측 상단과 우측 상단으로 분기됩니다. 세 개의 방향으로 연결되며, 중앙 교차점을 중심으로 120도 간격으로 배치됩니다. 2차선 도로로 구성되며, 속도는 50km/h(13.89m/s)입니다.',
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
    <!-- 하단에서 중앙으로 -->
    <edge id="bottom_to_center" from="bottom" to="center" priority="2" numLanes="2" speed="13.89"/>

    <!-- 중앙에서 하단으로 -->
    <edge id="center_to_bottom" from="center" to="bottom" priority="2" numLanes="2" speed="13.89"/>

    <!-- 중앙에서 좌측 상단으로 -->
    <edge id="center_to_top_left" from="center" to="top_left" priority="2" numLanes="2" speed="13.89"/>

    <!-- 좌측 상단에서 중앙으로 -->
    <edge id="top_left_to_center" from="top_left" to="center" priority="2" numLanes="2" speed="13.89"/>

    <!-- 중앙에서 우측 상단으로 -->
    <edge id="center_to_top_right" from="center" to="top_right" priority="2" numLanes="2" speed="13.89"/>

    <!-- 우측 상단에서 중앙으로 -->
    <edge id="top_right_to_center" from="top_right" to="center" priority="2" numLanes="2" speed="13.89"/>
</edges>`,
    tags: 'Y자 교차로,삼거리,분기 지점,양갈래 도로',
    category: 'junction',
    difficulty: 'medium'
  },
  {
    name: 't_junction_01',
    description: 'T자 모양의 삼거리 교차로입니다. 좌우로 이어지는 주 도로에 하단에서 올라오는 도로가 수직으로 연결됩니다. 세 개의 방향으로 연결되며, 일반적인 T자형 골목길이나 지선 도로 연결에 사용됩니다. 2차선 도로로 구성되며, 속도는 50km/h(13.89m/s)입니다.',
    nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- T형 교차로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <!-- 중앙 교차로 노드 -->
    <node id="center" x="0.0" y="0.0" type="priority"/>

    <!-- 좌측 노드 -->
    <node id="left" x="-100.0" y="0.0" type="priority"/>

    <!-- 우측 노드 -->
    <node id="right" x="100.0" y="0.0" type="priority"/>

    <!-- 하단 노드 -->
    <node id="bottom" x="0.0" y="-100.0" type="priority"/>
</nodes>`,
    edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- T형 교차로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <!-- 좌측에서 중앙으로 -->
    <edge id="left_to_center" from="left" to="center" priority="2" numLanes="2" speed="13.89"/>

    <!-- 중앙에서 좌측으로 -->
    <edge id="center_to_left" from="center" to="left" priority="2" numLanes="2" speed="13.89"/>

    <!-- 중앙에서 우측으로 -->
    <edge id="center_to_right" from="center" to="right" priority="2" numLanes="2" speed="13.89"/>

    <!-- 우측에서 중앙으로 -->
    <edge id="right_to_center" from="right" to="center" priority="2" numLanes="2" speed="13.89"/>

    <!-- 하단에서 중앙으로 -->
    <edge id="bottom_to_center" from="bottom" to="center" priority="2" numLanes="2" speed="13.89"/>

    <!-- 중앙에서 하단으로 -->
    <edge id="center_to_bottom" from="center" to="bottom" priority="2" numLanes="2" speed="13.89"/>
</edges>`,
    tags: 'T자 교차로,삼거리,직각 분기,측면 진입로',
    category: 'junction',
    difficulty: 'medium'
  },
  {
    name: 'three_lane_road_01',
    description: '넓은 3차선 직선 도로입니다. 200m 길이의 일직선 도로로 양방향 모두 3차선입니다. 속도는 80km/h(22.22m/s)로 고속 주행이 가능합니다. 교통량이 많은 주요 간선도로나 고속화도로에 적합합니다.',
    nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 3차선 직선 도로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <!-- 시작 노드 -->
    <node id="start" x="0.0" y="0.0" type="priority"/>

    <!-- 종료 노드 -->
    <node id="end" x="200.0" y="0.0" type="priority"/>
</nodes>`,
    edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 3차선 직선 도로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <!-- 시작에서 종료로 (3차선) -->
    <edge id="start_to_end" from="start" to="end" priority="3" numLanes="3" speed="22.22"/>

    <!-- 종료에서 시작으로 (3차선) -->
    <edge id="end_to_start" from="end" to="start" priority="3" numLanes="3" speed="22.22"/>
</edges>`,
    tags: '3차선,넓은 도로,간선도로,주요 도로,고속 도로,다차선 도로',
    category: 'highway',
    difficulty: 'easy'
  },
  {
    name: 'straight_road_01',
    description: '단순한 직선 도로입니다. 300m 길이의 긴 일직선 도로로 양방향 2차선입니다. 속도는 50km/h(13.89m/s)입니다. 가장 기본적인 도로 형태로, 복잡한 교차로 없이 단순 이동 경로가 필요할 때 적합합니다.',
    nodeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 1자형 직선 도로를 위한 Node 정의 -->
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <!-- 시작 노드 -->
    <node id="start" x="0.0" y="0.0" type="priority"/>

    <!-- 종료 노드 -->
    <node id="end" x="300.0" y="0.0" type="priority"/>
</nodes>`,
    edgeXml: `<?xml version="1.0" encoding="UTF-8"?>
<!-- 1자형 직선 도로를 위한 Edge 정의 -->
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <!-- 시작에서 종료로 -->
    <edge id="start_to_end" from="start" to="end" priority="2" numLanes="2" speed="13.89"/>

    <!-- 종료에서 시작으로 -->
    <edge id="end_to_start" from="end" to="start" priority="2" numLanes="2" speed="13.89"/>
</edges>`,
    tags: '1자형,직선 도로,단순 도로,일반 도로,기본 간선',
    category: 'general',
    difficulty: 'easy'
  }
];

async function importMaps() {
  console.log('🚀 맵 Import 시작...');

  for (const map of maps) {
    try {
      const result = await invoke('create_map', {
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

      console.log(`✅ ${map.name} 저장 완료 (ID: ${result.id})`);
    } catch (error) {
      console.error(`❌ ${map.name} 저장 실패:`, error);
    }
  }

  console.log('🎉 모든 맵 Import 완료!');
}

// 실행
importMaps();
