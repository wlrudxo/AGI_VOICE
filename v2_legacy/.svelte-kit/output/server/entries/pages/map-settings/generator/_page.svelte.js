import { Y as attr, X as ensure_array_like, _ as stringify, V as store_get, Z as unsubscribe_stores } from "../../../../chunks/index2.js";
import "@tauri-apps/api/core";
import "@tauri-apps/plugin-fs";
import "@tauri-apps/plugin-dialog";
import { p as page } from "../../../../chunks/stores.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { D as Dialog } from "../../../../chunks/Dialog.js";
function MapCanvas($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { nodes = [], edges = [] } = $$props;
    let canvasWidth = 800;
    let canvasHeight = 600;
    let mapBounds = calculateBounds(nodes);
    let viewBox = calculateViewBox(mapBounds, canvasWidth, canvasHeight);
    function calculateBounds(nodeList) {
      if (!nodeList || nodeList.length === 0) {
        return { minX: -100, maxX: 100, minY: -100, maxY: 100 };
      }
      let minX = Infinity, maxX = -Infinity;
      let minY = Infinity, maxY = -Infinity;
      nodeList.forEach((node) => {
        minX = Math.min(minX, node.x);
        maxX = Math.max(maxX, node.x);
        minY = Math.min(minY, node.y);
        maxY = Math.max(maxY, node.y);
      });
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
      const scaleX = width / mapWidth;
      const scaleY = height / mapHeight;
      const fitScale = Math.min(scaleX, scaleY) * 0.9;
      const centerX = (bounds.minX + bounds.maxX) / 2;
      const centerY = (bounds.minY + bounds.maxY) / 2;
      return {
        x: centerX - width / (2 * fitScale),
        y: centerY - height / (2 * fitScale),
        width: width / fitScale,
        height: height / fitScale
      };
    }
    function transformCoords(x, y) {
      return {
        x,
        y: -y
        // Flip Y-axis (SVG y goes down, map y goes up)
      };
    }
    function getNode(nodeId) {
      return nodes.find((n) => n.id === nodeId);
    }
    function getEdgePath(edge) {
      const fromNode = getNode(edge.from);
      const toNode = getNode(edge.to);
      if (!fromNode || !toNode) return "";
      const from = transformCoords(fromNode.x, fromNode.y);
      const to = transformCoords(toNode.x, toNode.y);
      return `M ${from.x} ${from.y} L ${to.x} ${to.y}`;
    }
    function getArrowTransform(edge) {
      const fromNode = getNode(edge.from);
      const toNode = getNode(edge.to);
      if (!fromNode || !toNode) return "";
      const from = transformCoords(fromNode.x, fromNode.y);
      const to = transformCoords(toNode.x, toNode.y);
      const midX = (from.x + to.x) / 2;
      const midY = (from.y + to.y) / 2;
      const dx = to.x - from.x;
      const dy = to.y - from.y;
      const angle = Math.atan2(dy, dx) * 180 / Math.PI;
      return `translate(${midX}, ${midY}) rotate(${angle})`;
    }
    function getNodeColor(type) {
      switch (type) {
        case "traffic_light":
          return "var(--color-error)";
        case // red
        "priority":
          return "var(--color-primary)";
        case // blue
        "right_before_left":
          return "var(--color-success)";
        default:
          return "var(--color-text-muted)";
      }
    }
    $$renderer2.push(`<div class="map-canvas svelte-4tz69q">`);
    if (nodes.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="empty-state svelte-4tz69q">`);
      Icon($$renderer2, { icon: "solar:map-bold-duotone", width: "64", height: "64" });
      $$renderer2.push(`<!----> <p class="svelte-4tz69q">노드 데이터가 없습니다</p> <p class="hint svelte-4tz69q">XML을 입력하고 미리보기 버튼을 눌러주세요</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<svg width="100%" height="100%"${attr("viewBox", `${stringify(viewBox.x)} ${stringify(viewBox.y)} ${stringify(viewBox.width)} ${stringify(viewBox.height)}`)} preserveAspectRatio="xMidYMid meet" class="svelte-4tz69q"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--color-border)" stroke-width="0.5"></path></pattern><marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="var(--color-text-secondary)"></path></marker></defs><rect${attr("x", viewBox.x)}${attr("y", viewBox.y)}${attr("width", viewBox.width)}${attr("height", viewBox.height)} fill="url(#grid)"></rect><g class="edges"><!--[-->`);
      const each_array = ensure_array_like(edges);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let edge = each_array[$$index];
        $$renderer2.push(`<path${attr("d", getEdgePath(edge))} stroke="var(--color-text-secondary)" stroke-width="2" fill="none" marker-mid="url(#arrowhead)" opacity="0.6"></path><g${attr("transform", getArrowTransform(edge))}><circle r="3" fill="var(--color-text-secondary)"></circle></g>`);
      }
      $$renderer2.push(`<!--]--></g><g class="nodes"><!--[-->`);
      const each_array_1 = ensure_array_like(nodes);
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let node = each_array_1[$$index_1];
        const coords = transformCoords(node.x, node.y);
        $$renderer2.push(`<g class="node svelte-4tz69q"><circle${attr("cx", coords.x)}${attr("cy", coords.y)} r="8"${attr("fill", getNodeColor(node.type))} stroke="white" stroke-width="2"></circle><text${attr("x", coords.x)}${attr("y", coords.y - 15)} text-anchor="middle" font-size="10" font-weight="600" fill="var(--color-text-primary)">${escape_html(node.id)}</text><text${attr("x", coords.x)}${attr("y", coords.y + 20)} text-anchor="middle" font-size="8" fill="var(--color-text-muted)">${escape_html(node.type)}</text></g>`);
      }
      $$renderer2.push(`<!--]--></g></svg> <div class="controls svelte-4tz69q"><button class="control-btn svelte-4tz69q" title="화면 초기화">`);
      Icon($$renderer2, { icon: "solar:restart-bold", width: "16", height: "16" });
      $$renderer2.push(`<!----></button></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let mapName = "";
    let mapDescription = "";
    let mapTags = "";
    let nodeXml = `<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="center" x="0.0" y="0.0" type="traffic_light"/>
    <node id="north" x="0.0" y="100.0" type="priority"/>
    <node id="south" x="0.0" y="-100.0" type="priority"/>
    <node id="east" x="100.0" y="0.0" type="priority"/>
    <node id="west" x="-100.0" y="0.0" type="priority"/>
</nodes>`;
    let edgeXml = `<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="north_to_center" from="north" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_north" from="center" to="north" priority="3" numLanes="2" speed="13.89"/>
    <edge id="south_to_center" from="south" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_south" from="center" to="south" priority="3" numLanes="2" speed="13.89"/>
    <edge id="east_to_center" from="east" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_east" from="center" to="east" priority="3" numLanes="2" speed="13.89"/>
    <edge id="west_to_center" from="west" to="center" priority="3" numLanes="2" speed="13.89"/>
    <edge id="center_to_west" from="center" to="west" priority="3" numLanes="2" speed="13.89"/>
</edges>`;
    let parsedNodes = [];
    let parsedEdges = [];
    const editMapId = (() => {
      const urlId = store_get($$store_subs ??= {}, "$page", page).url.searchParams.get("id");
      return urlId ? parseInt(urlId) : null;
    })();
    const isEditMode = editMapId !== null;
    Dialog($$renderer2, {});
    $$renderer2.push(`<!----> <div class="page-container svelte-14mb5b7"><div class="page-header"><div><h1>${escape_html(isEditMode ? "Map 수정" : "Map 생성")}</h1> <p class="page-description">${escape_html(isEditMode ? "SUMO XML 노드와 엣지를 수정하고 저장합니다." : "SUMO XML 노드와 엣지를 입력하여 맵을 생성하고 시각화합니다.")}</p></div> <div class="header-actions"><button class="btn-secondary">`);
    Icon($$renderer2, { icon: "solar:import-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> Import</button> <button class="btn-secondary">`);
    Icon($$renderer2, { icon: "solar:refresh-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> 미리보기</button> `);
    if (isEditMode) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<button class="btn-danger">`);
      Icon($$renderer2, {
        icon: "solar:trash-bin-trash-bold",
        width: "20",
        height: "20"
      });
      $$renderer2.push(`<!----> 삭제</button> <button class="btn-primary">`);
      Icon($$renderer2, { icon: "solar:diskette-bold", width: "20", height: "20" });
      $$renderer2.push(`<!----> 저장</button>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<button class="btn-primary">`);
      Icon($$renderer2, { icon: "solar:diskette-bold", width: "20", height: "20" });
      $$renderer2.push(`<!----> DB 저장</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="content-grid svelte-14mb5b7"><div class="input-panel svelte-14mb5b7"><div class="form-group"><label class="form-label">`);
    Icon($$renderer2, {
      icon: "solar:document-text-bold-duotone",
      width: "20",
      height: "20"
    });
    $$renderer2.push(`<!----> 맵 이름</label> <input type="text"${attr("value", mapName)} placeholder="예: crossroad_01" class="input-field w-full"/></div> <div class="form-group"><label class="form-label">`);
    Icon($$renderer2, { icon: "solar:text-bold-duotone", width: "20", height: "20" });
    $$renderer2.push(`<!----> 맵 설명</label> <textarea placeholder="RAG 검색에 사용될 맵 설명을 입력하세요. 예: 신호등이 있는 4거리 교차로. 2차선 도로가 십자형으로 교차함." rows="3" class="textarea-field w-full">`);
    const $$body = escape_html(mapDescription);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea></div> <div class="form-group"><label class="form-label">`);
    Icon($$renderer2, { icon: "solar:tag-bold-duotone", width: "20", height: "20" });
    $$renderer2.push(`<!----> 태그</label> <input type="text"${attr("value", mapTags)} placeholder="쉼표로 구분하여 입력하세요. 예: 교차로, 신호등, 4거리" class="input-field w-full"/> <p class="form-hint">태그는 쉼표(,)로 구분하여 입력하세요.</p></div> <div class="form-group"><label class="form-label">`);
    Icon($$renderer2, {
      icon: "solar:point-on-map-bold-duotone",
      width: "20",
      height: "20"
    });
    $$renderer2.push(`<!----> Node XML</label> <textarea placeholder="노드 XML을 입력하세요..." rows="12" class="textarea-field w-full">`);
    const $$body_1 = escape_html(nodeXml);
    if ($$body_1) {
      $$renderer2.push(`${$$body_1}`);
    }
    $$renderer2.push(`</textarea></div> <div class="form-group"><label class="form-label">`);
    Icon($$renderer2, { icon: "solar:route-bold-duotone", width: "20", height: "20" });
    $$renderer2.push(`<!----> Edge XML</label> <textarea placeholder="엣지 XML을 입력하세요..." rows="12" class="textarea-field w-full">`);
    const $$body_2 = escape_html(edgeXml);
    if ($$body_2) {
      $$renderer2.push(`${$$body_2}`);
    }
    $$renderer2.push(`</textarea></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="preview-panel svelte-14mb5b7"><div class="preview-header svelte-14mb5b7">`);
    Icon($$renderer2, { icon: "solar:eye-bold-duotone", width: "20", height: "20" });
    $$renderer2.push(`<!----> <span>맵 미리보기</span></div> <div class="canvas-wrapper svelte-14mb5b7">`);
    MapCanvas($$renderer2, { nodes: parsedNodes, edges: parsedEdges });
    $$renderer2.push(`<!----></div> <div class="stats svelte-14mb5b7"><div class="stat-item svelte-14mb5b7">`);
    Icon($$renderer2, { icon: "solar:point-on-map-bold", width: "16", height: "16" });
    $$renderer2.push(`<!----> <span>노드: ${escape_html(parsedNodes.length)}개</span></div> <div class="stat-item svelte-14mb5b7">`);
    Icon($$renderer2, { icon: "solar:route-bold", width: "16", height: "16" });
    $$renderer2.push(`<!----> <span>엣지: ${escape_html(parsedEdges.length)}개</span></div></div></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
