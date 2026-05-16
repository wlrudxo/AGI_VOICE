const state = {
  mode: "select",
  selected: null,
  edgeStart: null,
  drag: null,
  pan: null,
  suppressClick: false,
  viewBox: { x: -320, y: -230, width: 640, height: 460 },
  nodes: [],
  edges: [],
};

const svg = document.querySelector("#graphSvg");
const gridLayer = document.querySelector("#gridLayer");
const edgeLayer = document.querySelector("#edgeLayer");
const nodeLayer = document.querySelector("#nodeLayer");
const hintLayer = document.querySelector("#hintLayer");
const logBox = document.querySelector("#logBox");
const resultLinks = document.querySelector("#resultLinks");

const fields = {
  projectName: document.querySelector("#projectName"),
  health: document.querySelector("#health"),
  defaultLanes: document.querySelector("#defaultLanes"),
  defaultSpeed: document.querySelector("#defaultSpeed"),
  defaultTwoWay: document.querySelector("#defaultTwoWay"),
  emptyInspector: document.querySelector("#emptyInspector"),
  nodeInspector: document.querySelector("#nodeInspector"),
  edgeInspector: document.querySelector("#edgeInspector"),
  nodeId: document.querySelector("#nodeId"),
  nodeX: document.querySelector("#nodeX"),
  nodeY: document.querySelector("#nodeY"),
  nodeType: document.querySelector("#nodeType"),
  edgeId: document.querySelector("#edgeId"),
  edgeFrom: document.querySelector("#edgeFrom"),
  edgeTo: document.querySelector("#edgeTo"),
  edgeLanes: document.querySelector("#edgeLanes"),
  edgeSpeed: document.querySelector("#edgeSpeed"),
  edgeTwoWay: document.querySelector("#edgeTwoWay"),
  nodeCount: document.querySelector("#nodeCount"),
  edgeCount: document.querySelector("#edgeCount"),
  canvasHelp: document.querySelector("#canvasHelp"),
};

function nodeById(id) {
  return state.nodes.find((node) => node.id === id);
}

function edgeById(id) {
  return state.edges.find((edge) => edge.id === id);
}

function svgClientPoint(evt) {
  const pt = svg.createSVGPoint();
  pt.x = evt.clientX;
  pt.y = evt.clientY;
  const transformed = pt.matrixTransform(svg.getScreenCTM().inverse());
  return { x: transformed.x, y: transformed.y };
}

function svgPoint(evt) {
  const transformed = svgClientPoint(evt);
  return { x: Math.round(transformed.x), y: Math.round(-transformed.y) };
}

function applyViewBox() {
  const { x, y, width, height } = state.viewBox;
  svg.setAttribute("viewBox", `${x} ${y} ${width} ${height}`);
}

function resetView() {
  state.viewBox = { x: -320, y: -230, width: 640, height: 460 };
  state.pan = null;
  state.suppressClick = false;
  applyViewBox();
}

function niceGridStep() {
  const pixelsPerUnit = Math.max(svg.clientWidth || 1, 1) / Math.max(state.viewBox.width, 1);
  const rawStep = 48 / pixelsPerUnit;
  for (const step of [5, 10, 20, 50, 100, 200, 500, 1000]) {
    if (step >= rawStep) return step;
  }
  return 2000;
}

function zoomAt(evt) {
  evt.preventDefault();
  const oldBox = { ...state.viewBox };
  const point = svgClientPoint(evt);
  const factor = evt.deltaY < 0 ? 0.87 : 1 / 0.87;
  const nextWidth = Math.max(80, Math.min(5000, oldBox.width * factor));
  const nextHeight = Math.max(60, Math.min(3600, oldBox.height * factor));
  const ratioX = (point.x - oldBox.x) / oldBox.width;
  const ratioY = (point.y - oldBox.y) / oldBox.height;
  state.viewBox = {
    x: point.x - ratioX * nextWidth,
    y: point.y - ratioY * nextHeight,
    width: nextWidth,
    height: nextHeight,
  };
  applyViewBox();
  render();
}

function worldPath(fromNode, toNode) {
  return `M ${fromNode.x} ${-fromNode.y} L ${toNode.x} ${-toNode.y}`;
}

function uniqueNodeId() {
  let index = state.nodes.length + 1;
  while (nodeById(`N${index}`)) index += 1;
  return `N${index}`;
}

function uniqueEdgeId(fromId, toId) {
  const base = `E_${fromId}_${toId}`;
  let id = base;
  let index = 2;
  while (edgeById(id)) {
    id = `${base}_${index}`;
    index += 1;
  }
  return id;
}

function setMode(mode) {
  state.mode = mode;
  state.edgeStart = null;
  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  fields.canvasHelp.textContent =
    mode === "node"
      ? "노드 모드: 빈 공간 클릭으로 노드 추가"
      : mode === "edge"
        ? "엣지 모드: 시작 노드와 끝 노드를 차례로 클릭"
        : "선택 모드: 노드 드래그, 엣지/노드 클릭 편집";
  render();
}

function select(kind, id) {
  state.selected = kind && id ? { kind, id } : null;
  render();
}

function addNode(x, y, id = uniqueNodeId(), type = "") {
  state.nodes.push({ id, x, y, type });
  select("node", id);
}

function addEdge(from, to, options = {}) {
  if (from === to) return;
  const id = options.id || uniqueEdgeId(from, to);
  state.edges.push({
    id,
    from,
    to,
    numLanes: Number(options.numLanes || fields.defaultLanes.value || 1),
    speedKmh: Number(options.speedKmh || fields.defaultSpeed.value || 50),
    twoWay: options.twoWay ?? fields.defaultTwoWay.checked,
  });
  select("edge", id);
}

function drawGrid() {
  gridLayer.innerHTML = "";
  const ns = "http://www.w3.org/2000/svg";
  const step = niceGridStep();
  const minX = Math.floor(state.viewBox.x / step) * step;
  const maxX = Math.ceil((state.viewBox.x + state.viewBox.width) / step) * step;
  const minY = Math.floor(state.viewBox.y / step) * step;
  const maxY = Math.ceil((state.viewBox.y + state.viewBox.height) / step) * step;
  for (let x = minX; x <= maxX; x += step) {
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", x);
    line.setAttribute("y1", minY);
    line.setAttribute("x2", x);
    line.setAttribute("y2", maxY);
    line.setAttribute("class", x === 0 ? "axis-line" : "grid-line");
    gridLayer.appendChild(line);
  }
  for (let y = minY; y <= maxY; y += step) {
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", minX);
    line.setAttribute("y1", y);
    line.setAttribute("x2", maxX);
    line.setAttribute("y2", y);
    line.setAttribute("class", y === 0 ? "axis-line" : "grid-line");
    gridLayer.appendChild(line);
  }
}

function renderEdges() {
  edgeLayer.innerHTML = "";
  const ns = "http://www.w3.org/2000/svg";
  for (const edge of state.edges) {
    const fromNode = nodeById(edge.from);
    const toNode = nodeById(edge.to);
    if (!fromNode || !toNode) continue;
    const selected = state.selected?.kind === "edge" && state.selected.id === edge.id;

    const hit = document.createElementNS(ns, "path");
    hit.setAttribute("d", worldPath(fromNode, toNode));
    hit.setAttribute("class", "edge-hit");
    hit.addEventListener("click", (evt) => {
      evt.stopPropagation();
      select("edge", edge.id);
    });
    edgeLayer.appendChild(hit);

    const path = document.createElementNS(ns, "path");
    path.setAttribute("d", worldPath(fromNode, toNode));
    path.setAttribute("class", `edge-path${selected ? " selected" : ""}`);
    edgeLayer.appendChild(path);

    const midX = (fromNode.x + toNode.x) / 2;
    const midY = -(fromNode.y + toNode.y) / 2;
    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", midX);
    label.setAttribute("y", midY - 6);
    label.setAttribute("class", "edge-label");
    label.textContent = `${edge.id}${edge.twoWay ? " / 양방향" : ""}`;
    edgeLayer.appendChild(label);
  }
}

function renderNodes() {
  nodeLayer.innerHTML = "";
  const ns = "http://www.w3.org/2000/svg";
  for (const node of state.nodes) {
    const group = document.createElementNS(ns, "g");
    const selected = state.selected?.kind === "node" && state.selected.id === node.id;
    group.setAttribute("class", `node ${node.type || "priority"}${selected ? " selected" : ""}`);
    group.setAttribute("transform", `translate(${node.x}, ${-node.y})`);
    group.addEventListener("click", (evt) => handleNodeClick(evt, node.id));
    group.addEventListener("pointerdown", (evt) => handleNodePointerDown(evt, node.id));

    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("r", 14);
    group.appendChild(circle);

    if (node.type === "traffic_light" || node.type === "traffic_light_crosswalk") {
      [
        [-5, "#dc2626"],
        [0, "#facc15"],
        [5, "#22c55e"],
      ].forEach(([cy, fill]) => {
        const lamp = document.createElementNS(ns, "circle");
        lamp.setAttribute("cx", -7);
        lamp.setAttribute("cy", cy);
        lamp.setAttribute("r", 2.2);
        lamp.setAttribute("fill", fill);
        group.appendChild(lamp);
      });
    }

    if (node.type === "traffic_light_crosswalk" || node.type === "crosswalk") {
      [-5, 0, 5].forEach((y) => {
        const stripe = document.createElementNS(ns, "line");
        stripe.setAttribute("x1", 1);
        stripe.setAttribute("y1", y);
        stripe.setAttribute("x2", 12);
        stripe.setAttribute("y2", y);
        stripe.setAttribute("class", "node-crosswalk-stripe");
        group.appendChild(stripe);
      });
    }

    const text = document.createElementNS(ns, "text");
    text.textContent = node.id;
    group.appendChild(text);

    nodeLayer.appendChild(group);
  }
}

function renderHint() {
  hintLayer.innerHTML = "";
  if (state.mode !== "edge" || !state.edgeStart) return;
  const start = nodeById(state.edgeStart);
  if (!start) return;
  const ns = "http://www.w3.org/2000/svg";
  const circle = document.createElementNS(ns, "circle");
  circle.setAttribute("cx", start.x);
  circle.setAttribute("cy", -start.y);
  circle.setAttribute("r", 22);
  circle.setAttribute("fill", "none");
  circle.setAttribute("stroke", "#b45309");
  circle.setAttribute("stroke-width", "2");
  circle.setAttribute("stroke-dasharray", "5 5");
  hintLayer.appendChild(circle);
}

function renderInspector() {
  const node = state.selected?.kind === "node" ? nodeById(state.selected.id) : null;
  const edge = state.selected?.kind === "edge" ? edgeById(state.selected.id) : null;

  fields.emptyInspector.hidden = Boolean(node || edge);
  fields.nodeInspector.hidden = !node;
  fields.edgeInspector.hidden = !edge;

  if (node) {
    fields.nodeId.value = node.id;
    fields.nodeX.value = node.x;
    fields.nodeY.value = node.y;
    fields.nodeType.value = node.type || "";
  }

  if (edge) {
    fields.edgeId.value = edge.id;
    fields.edgeFrom.value = edge.from;
    fields.edgeTo.value = edge.to;
    fields.edgeLanes.value = edge.numLanes;
    fields.edgeSpeed.value = edge.speedKmh;
    fields.edgeTwoWay.checked = edge.twoWay;
  }

  fields.nodeCount.textContent = `${state.nodes.length} nodes`;
  fields.edgeCount.textContent = `${state.edges.length} edges`;
}

function render() {
  drawGrid();
  renderEdges();
  renderNodes();
  renderHint();
  renderInspector();
}

function handleNodeClick(evt, id) {
  evt.stopPropagation();
  if (state.mode === "edge") {
    if (!state.edgeStart) {
      state.edgeStart = id;
      select("node", id);
    } else {
      addEdge(state.edgeStart, id);
      state.edgeStart = null;
    }
    render();
    return;
  }
  select("node", id);
}

function handleNodePointerDown(evt, id) {
  if (state.mode !== "select") return;
  evt.preventDefault();
  evt.stopPropagation();
  const node = nodeById(id);
  const point = svgPoint(evt);
  state.drag = { id, dx: node.x - point.x, dy: node.y - point.y };
  select("node", id);
  svg.setPointerCapture(evt.pointerId);
}

function updateNodeFromInspector() {
  const node = state.selected?.kind === "node" ? nodeById(state.selected.id) : null;
  if (!node) return;
  const nextId = fields.nodeId.value.trim();
  if (nextId && nextId !== node.id && !nodeById(nextId)) {
    for (const edge of state.edges) {
      if (edge.from === node.id) edge.from = nextId;
      if (edge.to === node.id) edge.to = nextId;
    }
    state.selected.id = nextId;
    node.id = nextId;
  }
  node.x = Number(fields.nodeX.value || 0);
  node.y = Number(fields.nodeY.value || 0);
  node.type = fields.nodeType.value;
  render();
}

function updateEdgeFromInspector() {
  const edge = state.selected?.kind === "edge" ? edgeById(state.selected.id) : null;
  if (!edge) return;
  const nextId = fields.edgeId.value.trim();
  if (nextId && nextId !== edge.id && !edgeById(nextId)) {
    state.selected.id = nextId;
    edge.id = nextId;
  }
  edge.numLanes = Number(fields.edgeLanes.value || 1);
  edge.speedKmh = Number(fields.edgeSpeed.value || 50);
  edge.twoWay = fields.edgeTwoWay.checked;
  render();
}

function deleteSelected() {
  if (!state.selected) return;
  if (state.selected.kind === "node") {
    const id = state.selected.id;
    state.nodes = state.nodes.filter((node) => node.id !== id);
    state.edges = state.edges.filter((edge) => edge.from !== id && edge.to !== id);
  } else {
    state.edges = state.edges.filter((edge) => edge.id !== state.selected.id);
  }
  select(null, null);
}

function clearGraph() {
  state.nodes = [];
  state.edges = [];
  state.selected = null;
  state.edgeStart = null;
  resetView();
  resultLinks.innerHTML = "";
  logBox.textContent = "그래프가 초기화되었습니다.";
  render();
}

function loadTemplate(name) {
  clearGraph();
  fields.projectName.value = `${name}_demo`;
  const speedKmh = Number(fields.defaultSpeed.value || 50);
  const numLanes = Number(fields.defaultLanes.value || 1);

  const templates = {
    figure8: {
      nodes: [
        ["N_center", 0, 0, "priority"],
        ["N_left_top", -90, 80, ""],
        ["N_left", -160, 0, ""],
        ["N_left_bottom", -90, -80, ""],
        ["N_right_top", 90, 80, ""],
        ["N_right", 160, 0, ""],
        ["N_right_bottom", 90, -80, ""],
      ],
      edges: [
        ["E_center_left_top", "N_center", "N_left_top"],
        ["E_left_top_left", "N_left_top", "N_left"],
        ["E_left_left_bottom", "N_left", "N_left_bottom"],
        ["E_left_bottom_center", "N_left_bottom", "N_center"],
        ["E_center_right_top", "N_center", "N_right_top"],
        ["E_right_top_right", "N_right_top", "N_right"],
        ["E_right_right_bottom", "N_right", "N_right_bottom"],
        ["E_right_bottom_center", "N_right_bottom", "N_center"],
      ],
    },
    nine: {
      nodes: [
        ["N_top", 0, 120, ""],
        ["N_right", 110, 70, ""],
        ["N_mid", 85, -15, "priority"],
        ["N_left", -25, -15, ""],
        ["N_loop", -55, 70, ""],
        ["N_tail_mid", 85, -115, ""],
        ["N_tail_end", 85, -200, ""],
      ],
      edges: [
        ["E_top_right", "N_top", "N_right"],
        ["E_right_mid", "N_right", "N_mid"],
        ["E_mid_left", "N_mid", "N_left"],
        ["E_left_loop", "N_left", "N_loop"],
        ["E_loop_top", "N_loop", "N_top"],
        ["E_mid_tail", "N_mid", "N_tail_mid"],
        ["E_tail_end", "N_tail_mid", "N_tail_end"],
      ],
    },
    y: {
      nodes: [
        ["N_center", 0, 0, "priority"],
        ["N_bottom", 0, -120, ""],
        ["N_left", -90, 90, ""],
        ["N_right", 90, 90, ""],
      ],
      edges: [
        ["E_bottom_center", "N_bottom", "N_center", 2],
        ["E_center_left", "N_center", "N_left"],
        ["E_center_right", "N_center", "N_right"],
      ],
    },
    t: {
      nodes: [
        ["N_left", -130, 0, ""],
        ["N_center", 0, 0, "priority"],
        ["N_right", 130, 0, ""],
        ["N_bottom", 0, -120, ""],
      ],
      edges: [
        ["E_left_center", "N_left", "N_center"],
        ["E_center_right", "N_center", "N_right"],
        ["E_bottom_center", "N_bottom", "N_center"],
      ],
    },
  };

  const template = templates[name];
  for (const [id, x, y, type] of template.nodes) addNode(x, y, id, type);
  state.selected = null;
  for (const [id, from, to, lanes] of template.edges) {
    addEdge(from, to, { id, numLanes: lanes || numLanes, speedKmh, twoWay: true });
  }
  state.selected = null;
  logBox.textContent = `${name} 프리셋을 불러왔습니다.`;
  render();
}

function graphPayload() {
  return {
    nodes: state.nodes.map((node) => ({ ...node })),
    edges: state.edges.map((edge) => ({ ...edge })),
  };
}

function saveGraph() {
  const data = {
    projectName: fields.projectName.value,
    graph: graphPayload(),
  };
  localStorage.setItem("roadGenApp.graph", JSON.stringify(data));
  logBox.textContent = "브라우저 저장소에 그래프를 저장했습니다.";
}

function loadGraph() {
  const raw = localStorage.getItem("roadGenApp.graph");
  if (!raw) {
    logBox.textContent = "저장된 그래프가 없습니다.";
    return;
  }
  const data = JSON.parse(raw);
  fields.projectName.value = data.projectName || "road_graph";
  state.nodes = data.graph?.nodes || [];
  state.edges = data.graph?.edges || [];
  state.selected = null;
  state.edgeStart = null;
  logBox.textContent = "저장된 그래프를 불러왔습니다.";
  render();
}

async function generate() {
  resultLinks.innerHTML = "";
  logBox.textContent = "SUMO netconvert 실행 중...";
  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        projectName: fields.projectName.value,
        graph: graphPayload(),
      }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "generation failed");
    const names = [
      ["graph.json", data.files.graph],
      ["node.xml", data.files.nodeXml],
      ["edge.xml", data.files.edgeXml],
      ["net.xml", data.files.netXml],
      ["xodr", data.files.xodr],
    ];
    for (const [label, href] of names) {
      const link = document.createElement("a");
      link.href = href;
      link.target = "_blank";
      link.textContent = label;
      resultLinks.appendChild(link);
    }
    logBox.textContent = [
      `생성 완료: ${data.project}`,
      `SUMO edge IDs: ${data.edgeIds.join(", ")}`,
      "",
      ...data.commands.map((item) => {
        const stderr = item.stderr?.trim();
        const stdout = item.stdout?.trim();
        return [`$ ${item.command}`, stdout, stderr].filter(Boolean).join("\n");
      }),
    ].join("\n");
  } catch (err) {
    logBox.textContent = `오류: ${err.message}`;
  }
}

async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    fields.health.innerHTML = data.netconvert
      ? `<span class="ok">netconvert 연결됨</span>`
      : `<span class="warn">netconvert 없음</span>`;
  } catch {
    fields.health.innerHTML = `<span class="error">서버 연결 안 됨</span>`;
  }
}

function bindEvents() {
  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => setMode(button.dataset.mode));
  });
  document.querySelectorAll("[data-template]").forEach((button) => {
    button.addEventListener("click", () => loadTemplate(button.dataset.template));
  });

  svg.addEventListener("click", (evt) => {
    if (state.suppressClick) {
      state.suppressClick = false;
      return;
    }
    if (evt.target !== svg) return;
    if (state.mode === "node") {
      const point = svgPoint(evt);
      addNode(point.x, point.y);
    } else {
      select(null, null);
    }
  });

  svg.addEventListener("wheel", zoomAt, { passive: false });

  svg.addEventListener("pointerdown", (evt) => {
    if (evt.target !== svg || state.mode !== "select") return;
    evt.preventDefault();
    state.pan = {
      pointerId: evt.pointerId,
      startClientX: evt.clientX,
      startClientY: evt.clientY,
      origin: { ...state.viewBox },
      moved: false,
    };
    svg.setPointerCapture(evt.pointerId);
  });

  svg.addEventListener("pointermove", (evt) => {
    if (state.pan) {
      const dx = evt.clientX - state.pan.startClientX;
      const dy = evt.clientY - state.pan.startClientY;
      state.pan.moved ||= Math.hypot(dx, dy) > 3;
      const scaleX = state.pan.origin.width / Math.max(svg.clientWidth || 1, 1);
      const scaleY = state.pan.origin.height / Math.max(svg.clientHeight || 1, 1);
      state.viewBox = {
        ...state.pan.origin,
        x: state.pan.origin.x - dx * scaleX,
        y: state.pan.origin.y - dy * scaleY,
      };
      applyViewBox();
      render();
      return;
    }
    if (!state.drag) return;
    const node = nodeById(state.drag.id);
    if (!node) return;
    const point = svgPoint(evt);
    node.x = point.x + state.drag.dx;
    node.y = point.y + state.drag.dy;
    render();
  });

  svg.addEventListener("pointerup", (evt) => {
    if (state.pan) {
      state.suppressClick = state.pan.moved;
      state.pan = null;
      if (svg.hasPointerCapture(evt.pointerId)) svg.releasePointerCapture(evt.pointerId);
    }
    state.drag = null;
  });

  document.querySelector("#deleteBtn").addEventListener("click", deleteSelected);
  document.querySelector("#clearBtn").addEventListener("click", clearGraph);
  document.querySelector("#saveBtn").addEventListener("click", saveGraph);
  document.querySelector("#loadBtn").addEventListener("click", loadGraph);
  document.querySelector("#generateBtn").addEventListener("click", generate);

  [fields.nodeId, fields.nodeX, fields.nodeY, fields.nodeType].forEach((input) => {
    input.addEventListener("change", updateNodeFromInspector);
  });
  [fields.edgeId, fields.edgeLanes, fields.edgeSpeed, fields.edgeTwoWay].forEach((input) => {
    input.addEventListener("change", updateEdgeFromInspector);
  });

  window.addEventListener("keydown", (evt) => {
    if (evt.key === "Delete" || evt.key === "Backspace") {
      const tag = document.activeElement?.tagName;
      if (tag !== "INPUT" && tag !== "SELECT") deleteSelected();
    }
    if (evt.key === "Escape") {
      state.edgeStart = null;
      select(null, null);
    }
  });
}

applyViewBox();
drawGrid();
bindEvents();
loadTemplate("figure8");
setMode("select");
checkHealth();
