import { Y as attr } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import "@tauri-apps/api/core";
import { I as Icon } from "../../../../chunks/Icon.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let loading = true;
    let showHelpModal = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="chat-settings-page svelte-96bjq4"><div class="page-header"><div><div class="title-row svelte-96bjq4"><h1>채팅 설정</h1> <button class="btn-icon help-btn">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></div> <p class="page-description">AI 채팅에서 사용할 기본 캐릭터와 시스템 템플릿을 선택하세요.</p></div> <button class="btn-primary"${attr("disabled", loading, true)}>`);
      Icon($$renderer3, { icon: "solar:diskette-bold", width: "20", height: "20" });
      $$renderer3.push(`<!----> ${escape_html("저장")}</button></div> `);
      {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<div class="loading-state">`);
        Icon($$renderer3, { icon: "solar:ufo-2-duotone", width: "48", class: "spin" });
        $$renderer3.push(`<!----> <p>설정 로딩 중...</p></div>`);
      }
      $$renderer3.push(`<!--]--></div> `);
      HelpModal($$renderer3, {
        title: "채팅 설정 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>⚙️ 채팅 설정이란?</h4> <p class="help-desc">AI 채팅 위젯에서 사용할 기본 캐릭터와 시스템 템플릿을 설정합니다.
			이 설정은 새로운 대화를 시작할 때 자동으로 적용됩니다.</p></section> <section class="help-section"><h4>📋 설정 구성 요소</h4> <div class="command-example"><code>시스템 템플릿</code> <p>AI의 역할과 행동 방식을 정의하는 프롬프트입니다.
				예: "자율주행 연구 전문가", "일반 AI 어시스턴트" 등</p></div> <div class="command-example"><code>캐릭터</code> <p>AI의 말투, 성격, 톤을 정의합니다.
				예: "Research Assistant" - 전문적이고 친절한 톤</p></div></section> <section class="help-section"><h4>🔄 설정 적용 방법</h4> <ol class="help-list"><li><strong>시스템 템플릿</strong>과 <strong>캐릭터</strong>를 선택합니다.</li> <li><strong>설정 저장</strong> 버튼을 클릭합니다.</li> <li>채팅 위젯에서 새 대화를 시작하면 자동으로 적용됩니다.</li> <li>기존 대화는 설정 변경의 영향을 받지 않습니다.</li></ol></section> <section class="help-section"><h4>💡 Tip</h4> <ul class="help-list"><li>캐릭터와 템플릿은 <strong>AI 설정</strong> 메뉴에서 추가/수정/삭제할 수 있습니다.</li> <li>시스템 템플릿에서는 변수 치환을 지원합니다 (예: <code>{{user}}</code>, <code>{{char}}</code>).</li> <li>설정 변경은 즉시 채팅 위젯에 반영됩니다.</li></ul></section>`);
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
