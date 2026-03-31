import { Y as attr, X as ensure_array_like } from "../../../../chunks/index2.js";
import "@tauri-apps/api/core";
import { I as Icon } from "../../../../chunks/Icon.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let gasValue = 0;
    let brakeValue = 0;
    let steerValue = 0;
    let laneOffsetValue = 0;
    let targetVelocityValue = 0;
    let commandInput = "";
    let showHelpModal = false;
    let logMessages = [];
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="manual-control svelte-1ex915a"><div class="page-header"><div><h1>메뉴얼 제어</h1> <p class="page-description">차량을 수동으로 제어하고 명령을 실행합니다.</p></div></div> <section class="card section"><h2 class="section-title text-primary">`);
      Icon($$renderer3, {
        icon: "solar:steering-wheel-bold-duotone",
        width: "24",
        height: "24"
      });
      $$renderer3.push(`<!----> Driver Inputs</h2> <div class="control-row svelte-1ex915a"><label class="control-label svelte-1ex915a">Gas (0-1):</label> <input type="range" min="0" max="1" step="0.01"${attr("value", gasValue)} class="slider"/> <span class="value-display svelte-1ex915a">${escape_html(gasValue.toFixed(2))}</span> <button class="btn-primary btn-set svelte-1ex915a">Set</button></div> <div class="control-row svelte-1ex915a"><label class="control-label svelte-1ex915a">Brake (0-1):</label> <input type="range" min="0" max="1" step="0.01"${attr("value", brakeValue)} class="slider"/> <span class="value-display svelte-1ex915a">${escape_html(brakeValue.toFixed(2))}</span> <button class="btn-primary btn-set svelte-1ex915a">Set</button></div> <div class="control-row svelte-1ex915a"><label class="control-label svelte-1ex915a">Steer (-1~1):</label> <input type="range" min="-1" max="1" step="0.01"${attr("value", steerValue)} class="slider"/> <span class="value-display svelte-1ex915a">${escape_html(steerValue.toFixed(2))}</span> <button class="btn-primary btn-set svelte-1ex915a">Set</button></div> <div class="control-row svelte-1ex915a"><label class="control-label svelte-1ex915a">LaneOffset (-6.5~6.5):</label> <input type="range" min="-6.5" max="6.5" step="0.1"${attr("value", laneOffsetValue)} class="slider"/> <span class="value-display svelte-1ex915a">${escape_html(laneOffsetValue.toFixed(1))}</span> <button class="btn-primary btn-set svelte-1ex915a">Set</button></div> <div class="control-row svelte-1ex915a"><label class="control-label svelte-1ex915a">v.Trgt (0~50 m/s):</label> <input type="range" min="0" max="50" step="0.5"${attr("value", targetVelocityValue)} class="slider"/> <span class="value-display svelte-1ex915a">${escape_html(targetVelocityValue.toFixed(1))}</span> <button class="btn-primary btn-set svelte-1ex915a">Set</button></div></section> <section class="card section"><h2 class="section-title text-primary">`);
      Icon($$renderer3, { icon: "solar:code-bold-duotone", width: "24", height: "24" });
      $$renderer3.push(`<!----> Text Command Input <button class="btn-icon help-btn" title="도움말">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></h2> <div class="command-input-group svelte-1ex915a"><input type="text"${attr("value", commandInput)} placeholder="Enter command..." class="input-field command-input svelte-1ex915a"/> <button class="btn-primary">Execute</button></div></section> <section class="card section"><h2 class="section-title text-primary">`);
      Icon($$renderer3, {
        icon: "solar:document-text-bold-duotone",
        width: "24",
        height: "24"
      });
      $$renderer3.push(`<!----> Log</h2> <div class="log-container">`);
      if (logMessages.length === 0) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<p class="text-muted">No logs yet...</p>`);
      } else {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(logMessages);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let message = each_array[$$index];
          $$renderer3.push(`<div class="log-message text-secondary">${escape_html(message)}</div>`);
        }
        $$renderer3.push(`<!--]-->`);
      }
      $$renderer3.push(`<!--]--></div></section></div> `);
      HelpModal($$renderer3, {
        title: "Text Command 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>📋 명령어 형식</h4> <p class="help-desc">CarMaker APO 프로토콜을 사용하여 차량을 직접 제어할 수 있습니다.</p></section> <section class="help-section"><h4>🚗 차량 제어 명령어</h4> <div class="command-example"><code>DVAWrite DM.Gas 0.5 2000 Abs</code> <p>Gas 페달을 0.5로 2초간 설정</p></div> <div class="command-example"><code>DVAWrite DM.Brake 0.3 1500 Abs</code> <p>Brake 페달을 0.3으로 1.5초간 설정</p></div> <div class="command-example"><code>DVAWrite DM.Steer.Ang 0.2 3000 Abs</code> <p>조향각을 0.2 라디안으로 3초간 설정</p></div> <div class="command-example"><code>DVAWrite DM.v.Trgt 50 -1 Abs</code> <p>목표 속도를 50 m/s로 설정 (무한 지속: -1)</p></div> <div class="command-example"><code>DVAWrite DM.LaneOffset 0.5 5000 Abs</code> <p>차선 오프셋을 0.5m로 5초간 설정</p></div></section> <section class="help-section"><h4>⚙️ 시뮬레이션 제어</h4> <div class="command-example"><code>StartSim</code> <p>시뮬레이션 시작</p></div> <div class="command-example"><code>StopSim</code> <p>시뮬레이션 중지</p></div> <div class="command-example"><code>DVAWrite SC.TAccel 0.001 30000 Abs</code> <p>시간 가속도를 0.001로 설정 (일시정지 효과)</p></div></section> <section class="help-section"><h4>📊 변수 읽기</h4> <div class="command-example"><code>DVARead Car.v</code> <p>차량 속도 읽기 (m/s)</p></div> <div class="command-example"><code>DVARead Vhcl.sRoad</code> <p>도로 위치 S 좌표 읽기 (m)</p></div> <div class="command-example"><code>DVARead Traffic.nObjs</code> <p>주변 차량 수 읽기</p></div></section> <section class="help-section"><h4>📖 DVAWrite 파라미터</h4> <div class="param-table"><div class="param-row"><span class="param-name">Name</span> <span class="param-desc">변수명 (예: DM.Gas, DM.Brake)</span></div> <div class="param-row"><span class="param-name">Value</span> <span class="param-desc">설정할 값 (float)</span></div> <div class="param-row"><span class="param-name">Duration</span> <span class="param-desc">지속 시간 (ms), -1은 무한</span></div> <div class="param-row"><span class="param-name">Mode</span> <span class="param-desc"><strong>Abs</strong>: 절대값 (즉시 적용)<br/> <strong>AbsRamp</strong>: 부드러운 전환<br/> <strong>Fac</strong>: 배율</span></div></div></section> <section class="help-section"><h4>💡 초보자 권장 명령어</h4> <div class="command-example highlight"><code>DVAWrite DM.Gas 0.3 2000 Abs</code> <p>부드러운 가속 테스트</p></div> <div class="command-example highlight"><code>DVARead Car.v</code> <p>현재 속도 확인</p></div> <div class="command-example highlight"><code>DVAWrite DM.Brake 0.5 1000 Abs</code> <p>감속 테스트</p></div></section>`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!---->`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}
export {
  _page as default
};
