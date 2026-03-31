import { Y as attr, W as attr_class, X as ensure_array_like } from "../../../../chunks/index2.js";
import "@tauri-apps/api/core";
import { I as Icon } from "../../../../chunks/Icon.js";
import { c as carmakerStore } from "../../../../chunks/carmakerStore.svelte.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const controlModes = ["Abs", "Off", "Fac", "AbsRamp", "FacRamp"];
    const claudeModels = ["sonnet", "haiku", "opus"];
    let saving = false;
    let vehicleCommandParsingEnabled = false;
    let showMonitoringHelpModal = false;
    let showOneTimeHelpModal = false;
    let showChatSettingsHelpModal = false;
    let characters = [];
    let promptTemplates = [];
    let excludeHistory = true;
    let selectedCharacterId = null;
    let selectedPromptTemplateId = null;
    let selectedModel = "sonnet";
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="autonomous-settings svelte-1wj772t"><div class="page-header"><div><h1>자율주행 설정</h1> <p class="page-description">CarMaker 제어와 관련된 설정을 관리합니다.</p></div></div> <div class="settings-form svelte-1wj772t"><div class="form-section svelte-1wj772t"><h2 class="section-title">`);
      Icon($$renderer3, {
        icon: "solar:link-circle-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----> <span>CarMaker Connection</span></h2> <div class="connection-controls svelte-1wj772t"><div class="input-group svelte-1wj772t"><label for="host" class="svelte-1wj772t">Host:</label> <input id="host" type="text"${attr("value", carmakerStore.host)}${attr("disabled", carmakerStore.isConnected, true)} class="input-field"/></div> <div class="input-group svelte-1wj772t"><label for="port" class="svelte-1wj772t">Port:</label> <input id="port" type="text"${attr("value", carmakerStore.port)}${attr("disabled", carmakerStore.isConnected, true)} class="input-field"/></div> <button class="btn-primary"${attr("disabled", carmakerStore.isConnected, true)}>Connect</button> <button class="btn-secondary"${attr("disabled", !carmakerStore.isConnected, true)}>Disconnect</button> <div class="status-indicator"><span${attr_class("status-dot", void 0, { "connected": carmakerStore.isConnected })}></span> <span class="text-secondary">${escape_html(carmakerStore.isConnected ? "Connected" : "Disconnected")}</span></div></div></div></div> <div class="settings-form svelte-1wj772t"><div class="form-section svelte-1wj772t"><h2 class="section-title">`);
      Icon($$renderer3, {
        icon: "solar:settings-minimalistic-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----> <span>Control Settings</span></h2> <div class="settings-controls svelte-1wj772t"><div class="input-group svelte-1wj772t"><label for="duration" class="svelte-1wj772t">Duration (ms):</label> <input id="duration" type="text"${attr("value", carmakerStore.duration)} class="input-field"/></div> <div class="input-group svelte-1wj772t"><label for="mode" class="svelte-1wj772t">Control Mode:</label> `);
      $$renderer3.select(
        {
          id: "mode",
          value: carmakerStore.controlMode,
          class: "select-field"
        },
        ($$renderer4) => {
          $$renderer4.push(`<!--[-->`);
          const each_array = ensure_array_like(controlModes);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let mode = each_array[$$index];
            $$renderer4.option({ value: mode }, ($$renderer5) => {
              $$renderer5.push(`${escape_html(mode)}`);
            });
          }
          $$renderer4.push(`<!--]-->`);
        }
      );
      $$renderer3.push(`</div></div></div></div> <div class="settings-form svelte-1wj772t"><div class="form-section svelte-1wj772t"><h2 class="section-title">`);
      Icon($$renderer3, {
        icon: "solar:code-square-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----> <span>AI CarMaker Control</span></h2> <div class="toggle-row svelte-1wj772t"><div class="toggle-info svelte-1wj772t"><div class="label-with-help svelte-1wj772t"><label for="command-parsing" class="svelte-1wj772t">AI 자율주행 모니터링</label> <button class="btn-icon help-btn-inline">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "18",
        height: "18"
      });
      $$renderer3.push(`<!----></button></div></div> <label class="toggle-switch"><input id="command-parsing" type="checkbox"${attr("checked", vehicleCommandParsingEnabled, true)}/> <span class="toggle-switch-track"><span class="toggle-switch-thumb"></span></span></label></div> <div class="toggle-row svelte-1wj772t"><div class="toggle-info svelte-1wj772t"><div class="label-with-help svelte-1wj772t"><label for="exclude-history" class="svelte-1wj772t">일회용 메시지</label> <button class="btn-icon help-btn-inline">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "18",
        height: "18"
      });
      $$renderer3.push(`<!----></button></div></div> <label class="toggle-switch"><input id="exclude-history" type="checkbox"${attr("checked", excludeHistory, true)}/> <span class="toggle-switch-track"><span class="toggle-switch-thumb"></span></span></label></div> <div class="subsection svelte-1wj772t"><div class="subsection-header svelte-1wj772t"><h3 class="subsection-title svelte-1wj772t">`);
      Icon($$renderer3, {
        icon: "solar:chat-round-call-bold-duotone",
        width: "18",
        height: "18"
      });
      $$renderer3.push(`<!----> 대화 설정</h3> <button class="btn-icon help-btn-inline">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "18",
        height: "18"
      });
      $$renderer3.push(`<!----></button></div> <div class="ai-config-grid svelte-1wj772t"><div class="form-group svelte-1wj772t"><label for="trigger-template" class="svelte-1wj772t">시스템 템플릿</label> `);
      $$renderer3.select(
        {
          id: "trigger-template",
          value: selectedPromptTemplateId,
          class: "select-field"
        },
        ($$renderer4) => {
          $$renderer4.option({ value: null }, ($$renderer5) => {
            $$renderer5.push(`선택하세요`);
          });
          $$renderer4.push(`<!--[-->`);
          const each_array_1 = ensure_array_like(promptTemplates);
          for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
            let template = each_array_1[$$index_1];
            $$renderer4.option({ value: template.id }, ($$renderer5) => {
              $$renderer5.push(`${escape_html(template.name)}`);
            });
          }
          $$renderer4.push(`<!--]-->`);
        }
      );
      $$renderer3.push(`</div> <div class="form-group svelte-1wj772t"><label for="trigger-character" class="svelte-1wj772t">캐릭터</label> `);
      $$renderer3.select(
        {
          id: "trigger-character",
          value: selectedCharacterId,
          class: "select-field"
        },
        ($$renderer4) => {
          $$renderer4.option({ value: null }, ($$renderer5) => {
            $$renderer5.push(`선택하세요`);
          });
          $$renderer4.push(`<!--[-->`);
          const each_array_2 = ensure_array_like(characters);
          for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
            let character = each_array_2[$$index_2];
            $$renderer4.option({ value: character.id }, ($$renderer5) => {
              $$renderer5.push(`${escape_html(character.name)}`);
            });
          }
          $$renderer4.push(`<!--]-->`);
        }
      );
      $$renderer3.push(`</div> <div class="form-group svelte-1wj772t"><label for="trigger-model" class="svelte-1wj772t">모델</label> `);
      $$renderer3.select(
        {
          id: "trigger-model",
          value: selectedModel,
          class: "select-field"
        },
        ($$renderer4) => {
          $$renderer4.push(`<!--[-->`);
          const each_array_3 = ensure_array_like(claudeModels);
          for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
            let model = each_array_3[$$index_3];
            $$renderer4.option({ value: model }, ($$renderer5) => {
              $$renderer5.push(`${escape_html(model)}`);
            });
          }
          $$renderer4.push(`<!--]-->`);
        }
      );
      $$renderer3.push(`</div></div></div></div></div> `);
      {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--> <div class="form-actions svelte-1wj772t"><button type="button" class="btn-primary"${attr("disabled", saving, true)}>`);
      Icon($$renderer3, {
        icon: "solar:diskette-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----> <span>${escape_html("설정 저장")}</span></button></div></div> `);
      HelpModal($$renderer3, {
        title: "AI 자율주행 모니터링",
        onClose: () => showMonitoringHelpModal = false,
        get visible() {
          return showMonitoringHelpModal;
        },
        set visible($$value) {
          showMonitoringHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>🤖 AI 자율주행 모니터링이란?</h4> <p class="help-desc">AI 응답에서 차량 제어 명령을 자동으로 파싱하여 CarMaker에 실행합니다.
      트리거 발동 시 AI의 응답에 포함된 제어 명령을 자동으로 인식하고 실행합니다.</p></section> <section class="help-section"><h4>📋 명령 형식</h4> <p class="help-desc">AI 응답에 다음과 같은 형식의 명령을 포함하면 자동으로 파싱되어 실행됩니다.</p> <div class="command-example"><code>DM.Gas = 0.5</code> <p>가스 페달을 0.5로 설정 (범위: 0-1)</p></div> <div class="command-example"><code>DM.Brake = 0.3</code> <p>브레이크 페달을 0.3으로 설정 (범위: 0-1)</p></div> <div class="command-example"><code>DM.Steer.Ang = 0.1</code> <p>조향각을 0.1 라디안으로 설정</p></div></section> <section class="help-section"><h4>🔄 동작 방식</h4> <ol class="help-list"><li>트리거가 발동되면 AI에게 상황을 전달합니다.</li> <li>AI가 응답을 생성하며, 차량 제어 명령을 포함합니다.</li> <li>시스템이 응답에서 명령을 자동으로 추출합니다.</li> <li>추출된 명령을 CarMaker로 전송하여 실행합니다.</li></ol></section> <section class="help-section"><h4>⚠️ 사용 전 확인사항</h4> <ul class="help-list"><li><strong>CarMaker 연결</strong>이 필요합니다 (Connection 섹션에서 연결).</li> <li><strong>Vehicle Monitoring</strong>이 활성화되어야 합니다 (차량 제어 탭).</li> <li><strong>Trigger Monitoring</strong>은 별도로 제어됩니다 (트리거 설정 탭).</li> <li>이 토글은 AI 응답 파싱만 활성화/비활성화합니다.</li></ul></section>`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!----> `);
      HelpModal($$renderer3, {
        title: "일회용 메시지",
        onClose: () => showOneTimeHelpModal = false,
        get visible() {
          return showOneTimeHelpModal;
        },
        set visible($$value) {
          showOneTimeHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>💬 일회용 메시지란?</h4> <p class="help-desc">트리거가 발동될 때마다 AI에게 전송하는 메시지의 대화 기록 포함 여부를 설정합니다.</p></section> <section class="help-section"><h4>✅ 활성화 (일회용)</h4> <p class="help-desc">트리거 발동마다 <strong>이전 대화 기록 없이</strong> 새로운 요청을 보냅니다.</p> <div class="example-card svelte-1wj772t"><h5 class="svelte-1wj772t">장점</h5> <ul class="help-list"><li>매번 독립적인 판단을 받을 수 있습니다.</li> <li>이전 응답의 영향을 받지 않습니다.</li> <li>토큰 사용량이 적습니다.</li></ul></div> <div class="example-card svelte-1wj772t"><h5 class="svelte-1wj772t">사용 사례</h5> <p class="svelte-1wj772t">단순 규칙 기반 제어, 독립적인 판단이 필요한 경우</p></div></section> <section class="help-section"><h4>❌ 비활성화 (대화 누적)</h4> <p class="help-desc">트리거 발동마다 <strong>동일 대화방에 메시지가 누적</strong>됩니다.</p> <div class="example-card svelte-1wj772t"><h5 class="svelte-1wj772t">장점</h5> <ul class="help-list"><li>AI가 이전 상황을 기억합니다.</li> <li>연속적인 의사결정이 가능합니다.</li> <li>상황 변화를 추적할 수 있습니다.</li></ul></div> <div class="example-card svelte-1wj772t"><h5 class="svelte-1wj772t">사용 사례</h5> <p class="svelte-1wj772t">복잡한 시나리오, 상황 인식이 필요한 경우, 학습 기반 제어</p></div></section> <section class="help-section"><h4>💡 권장 설정</h4> <ul class="help-list"><li><strong>규칙 모드</strong> (규칙 제어 ON): 일회용 메시지 활성화 권장</li> <li><strong>LLM 모드</strong> (트리거만 ON): 대화 누적 권장 (상황 인식)</li></ul></section>`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!----> `);
      HelpModal($$renderer3, {
        title: "대화 설정",
        onClose: () => showChatSettingsHelpModal = false,
        get visible() {
          return showChatSettingsHelpModal;
        },
        set visible($$value) {
          showChatSettingsHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>⚙️ 대화 설정이란?</h4> <p class="help-desc">트리거 발동 시 AI와 대화할 때 사용할 시스템 템플릿, 캐릭터, 모델을 설정합니다.
      여기서 설정한 값은 트리거 전용으로 사용되며, 일반 채팅 위젯과는 별도로 동작합니다.</p></section> <section class="help-section"><h4>📋 설정 항목</h4> <div class="command-example"><code>시스템 템플릿</code> <p>AI의 역할과 행동 방식을 정의합니다.
        예: "자율주행 연구 전문가", "차량 제어 전문가"</p></div> <div class="command-example"><code>캐릭터</code> <p>AI의 말투, 성격, 톤을 정의합니다.
        예: "Research Assistant" - 전문적이고 친절한 톤</p></div> <div class="command-example"><code>모델</code> <p>사용할 Claude 모델을 선택합니다.
        - sonnet: 균형잡힌 성능 (권장)
        - haiku: 빠른 응답
        - opus: 고성능 (느림)</p></div></section> <section class="help-section"><h4>🔄 기본값 사용</h4> <p class="help-desc">시스템 템플릿 또는 캐릭터를 "선택하세요"로 두면, <strong>AI 설정</strong> 메뉴의 <strong>채팅 설정</strong>에서 지정한 기본값을 사용합니다.</p> <ul class="help-list"><li>트리거 전용 설정을 사용하려면 여기서 직접 선택</li> <li>일반 채팅과 동일한 설정을 사용하려면 "선택하세요" 유지</li></ul></section> <section class="help-section"><h4>💡 Tip</h4> <ul class="help-list"><li>시스템 템플릿과 캐릭터는 <strong>AI 설정</strong> 메뉴에서 추가/수정할 수 있습니다.</li> <li>트리거 전용 시스템 템플릿을 만들어두면 자율주행에 특화된 응답을 받을 수 있습니다.</li> <li>모델은 빠른 응답이 필요하면 haiku, 정확도가 중요하면 sonnet을 권장합니다.</li></ul></section>`);
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
