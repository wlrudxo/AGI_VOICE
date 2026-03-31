import { X as ensure_array_like, Y as attr, W as attr_class, _ as stringify } from "../../../../chunks/index2.js";
import "@tauri-apps/api/core";
import { I as Icon } from "../../../../chunks/Icon.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let triggers = [];
    let showHelpModal = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="trigger-settings svelte-1t19j6h"><div class="page-header"><div class="title-row svelte-1t19j6h"><h1>트리거 설정</h1> <button class="btn-icon help-btn">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></div> <div class="header-actions"><button class="btn-primary">`);
      Icon($$renderer3, { icon: "solar:add-circle-bold", width: "20", height: "20" });
      $$renderer3.push(`<!----> 새 트리거</button></div></div> `);
      {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<div class="triggers-list svelte-1t19j6h">`);
        if (triggers.length === 0) {
          $$renderer3.push("<!--[-->");
          $$renderer3.push(`<div class="empty-state card svelte-1t19j6h">`);
          Icon($$renderer3, {
            icon: "solar:atom-bold-duotone",
            width: "64",
            height: "64",
            class: "empty-icon"
          });
          $$renderer3.push(`<!----> <p class="text-secondary">등록된 트리거가 없습니다.</p> <button class="btn-primary">`);
          Icon($$renderer3, { icon: "solar:add-circle-bold", width: "20", height: "20" });
          $$renderer3.push(`<!----> 첫 트리거 만들기</button></div>`);
        } else {
          $$renderer3.push("<!--[!-->");
          $$renderer3.push(`<!--[-->`);
          const each_array = ensure_array_like(triggers);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let trigger = each_array[$$index];
            $$renderer3.push(`<div class="trigger-card card svelte-1t19j6h"><div class="trigger-header svelte-1t19j6h"><div class="trigger-title-row svelte-1t19j6h"><h3 class="trigger-name svelte-1t19j6h">${escape_html(trigger.name)}</h3> <div class="trigger-actions svelte-1t19j6h"><div class="toggle-group svelte-1t19j6h"><span class="toggle-label svelte-1t19j6h">트리거</span> <label class="toggle-switch"><input type="checkbox"${attr("checked", trigger.isActive, true)}/> <span class="toggle-switch-track"><span class="toggle-switch-thumb"></span></span></label></div> <div class="toggle-group svelte-1t19j6h"><span class="toggle-label svelte-1t19j6h">규칙</span> <label class="toggle-switch"><input type="checkbox"${attr("checked", trigger.useRuleControl, true)}/> <span class="toggle-switch-track"><span class="toggle-switch-thumb"></span></span></label></div> <button class="btn-icon">`);
            Icon($$renderer3, { icon: "solar:pen-bold", width: "20", height: "20" });
            $$renderer3.push(`<!----></button> <button class="btn-icon danger">`);
            Icon($$renderer3, {
              icon: "solar:trash-bin-trash-bold",
              width: "20",
              height: "20"
            });
            $$renderer3.push(`<!----></button></div></div> <div class="status-badges svelte-1t19j6h"><span${attr_class(`trigger-status ${stringify(trigger.isActive ? "active" : "inactive")}`, "svelte-1t19j6h")}>${escape_html(trigger.isActive ? "활성" : "비활성")}</span> `);
            if (trigger.useRuleControl) {
              $$renderer3.push("<!--[-->");
              $$renderer3.push(`<span class="trigger-status rule-control svelte-1t19j6h">규칙 제어</span>`);
            } else {
              $$renderer3.push("<!--[!-->");
            }
            $$renderer3.push(`<!--]--> <span class="trigger-status cooldown svelte-1t19j6h">쿨다운: ${escape_html((trigger.cooldown / 1e3).toFixed(1))}s</span></div></div> <div class="trigger-body svelte-1t19j6h"><div class="trigger-section svelte-1t19j6h"><h4 class="svelte-1t19j6h">발동 조건식</h4> <pre class="expression-preview svelte-1t19j6h">${escape_html(trigger.expression)}</pre></div> <div class="trigger-section svelte-1t19j6h"><h4 class="svelte-1t19j6h">LLM 메시지</h4> <p class="message-preview svelte-1t19j6h">${escape_html(trigger.message)}</p></div> `);
            if (trigger.debugAction) {
              $$renderer3.push("<!--[-->");
              $$renderer3.push(`<div class="trigger-section svelte-1t19j6h"><h4 class="svelte-1t19j6h">Action 예시</h4> <pre class="action-preview svelte-1t19j6h">${escape_html(trigger.debugAction)}</pre></div>`);
            } else {
              $$renderer3.push("<!--[!-->");
            }
            $$renderer3.push(`<!--]--></div></div>`);
          }
          $$renderer3.push(`<!--]-->`);
        }
        $$renderer3.push(`<!--]--></div>`);
      }
      $$renderer3.push(`<!--]--></div> `);
      HelpModal($$renderer3, {
        title: "트리거 설정 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>⚡ 트리거란?</h4> <p class="help-desc">트리거는 차량 데이터(속도, 조향각 등)가 특정 조건을 만족할 때 자동으로 LLM에 메시지를 전송하거나 규칙 기반 제어를 실행하는 시스템입니다.</p></section> <section class="help-section"><h4>🎯 트리거 구성 요소</h4> <ul class="help-list"><li><strong>이름</strong>: 트리거를 식별할 수 있는 이름</li> <li><strong>발동 조건</strong>: 차량 데이터 변수와 비교 연산자, 값으로 구성</li> <li><strong>논리 연산자</strong>: AND (모두 충족) 또는 OR (하나 이상 충족)</li> <li><strong>LLM 메시지</strong>: 조건 충족 시 LLM에 전송할 메시지</li> <li><strong>Action 예시</strong>: 규칙 제어 모드에서 실행할 명령</li> <li><strong>쿨다운</strong>: 발동 후 재발동까지 대기 시간 (기본 5000ms)</li></ul></section> <section class="help-section"><h4>🔧 동작 모드</h4> <div class="mode-card"><h5>📊 LLM 모드 (트리거 토글 ON, 규칙 토글 OFF)</h5> <p>1. 트리거 감지<br/> 2. 시뮬레이션 초감속 (0.001x)<br/> 3. LLM에 상황 전달 및 응답 대기<br/> 4. 시뮬레이션 정상 속도 (1.0x)<br/> 5. LLM 응답 파싱 및 명령 실행</p></div> <div class="mode-card"><h5>📝 규칙 모드 (규칙 토글 ON)</h5> <p>1. 트리거 감지<br/> 2. 시뮬레이션 초감속 (0.001x)<br/> 3. 1초 대기<br/> 4. 시뮬레이션 정상 속도 (1.0x)<br/> 5. Action 예시의 명령 실행</p></div></section> <section class="help-section"><h4>📋 Action 예시 형식</h4> <p class="help-desc">규칙 모드에서 실행할 차량 제어 명령을 작성합니다.</p> <div class="command-example"><code>DM.Gas = 0.5</code> <p>가스 페달을 0.5로 설정</p></div> <div class="command-example"><code>DM.Brake = 0.3</code> <p>브레이크 페달을 0.3으로 설정</p></div> <div class="command-example"><code>DM.Steer.Ang = 0.1</code> <p>조향각을 0.1 라디안으로 설정</p></div></section> <section class="help-section"><h4>📌 사용 예시</h4> <div class="example-card"><h5>속도 초과 감지 트리거</h5> <ul class="help-list"><li><strong>이름</strong>: 속도 초과 경고</li> <li><strong>조건</strong>: Car.v > 27.78 (100km/h 초과)</li> <li><strong>메시지</strong>: "차량 속도가 100km/h를 초과했습니다. 감속이 필요합니다."</li> <li><strong>Action</strong>:<br/> <code>DM.Gas = 0.0<br/>DM.Brake = 0.5</code></li></ul></div> <div class="example-card"><h5>추월 트리거 (전방 차량 접근)</h5> <ul class="help-list"><li><strong>이름</strong>: 추월</li> <li><strong>조건</strong>: (Traffic.T00.sRoad - Vhcl.sRoad) &lt; 40 &amp;&amp; (Traffic.T00.sRoad - Vhcl.sRoad) > 0</li> <li><strong>메시지</strong>: "전방 차량과의 거리가 가까워졌습니다. 추월하세요."</li></ul> <p class="help-warning svelte-1t19j6h">⚠️ <strong>> 0 조건 필수!</strong> 없으면 추월 후에도 트리거가 재발동됩니다. (음수도 &lt; 40 만족)</p></div></section> <section class="help-section"><h4>⚠️ 조건 작성 시 주의사항</h4> <ul class="help-list"><li><strong>범위 조건</strong>: 단순 비교만으로는 부족한 경우가 있습니다. 예: 거리 &lt; 40 → 음수도 포함됨</li> <li><strong>방향 고려</strong>: 전방/후방 판별이 필요하면 > 0 또는 &lt; 0 조건을 추가하세요</li> <li><strong>쿨다운</strong>: 트리거별로 설정 가능 (기본 5초). 트리거 발동 후 쿨다운 시간 동안 재발동 방지. 조건이 계속 만족되어도 쿨다운 중에는 무시됨</li> <li><strong>괄호 사용</strong>: 복잡한 조건은 괄호로 우선순위를 명확히 하세요</li></ul></section> <section class="help-section"><h4>⚙️ 모니터링 활성화</h4> <p class="help-desc">트리거를 사용하려면:</p> <ol class="help-list"><li>차량 제어 탭에서 CarMaker 연결</li> <li>차량 제어 탭에서 Vehicle Monitoring 시작</li> <li>트리거 설정 탭에서 "Start Trigger Monitoring" 클릭</li> <li>트리거 활성화 (트리거 토글 ON)</li></ol></section>`);
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
