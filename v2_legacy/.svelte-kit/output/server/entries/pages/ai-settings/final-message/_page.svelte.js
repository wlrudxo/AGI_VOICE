import { Y as attr } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let finalMessage = "";
    let isSaving = false;
    let showHelpModal = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="page-container svelte-famt8i"><div class="page-header"><div><div class="title-row svelte-famt8i"><h1>최종 메시지</h1> <button class="btn-icon help-btn">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></div> <p class="page-description">AI 응답 생성 전 마지막으로 체크할 사항을 입력하세요.</p></div> <div class="header-actions svelte-famt8i"><button class="btn-secondary">`);
      Icon($$renderer3, { icon: "solar:refresh-bold", width: "20", height: "20" });
      $$renderer3.push(`<!----> 초기화</button> <button class="btn-primary"${attr("disabled", isSaving, true)}>`);
      Icon($$renderer3, { icon: "solar:diskette-bold", width: "20", height: "20" });
      $$renderer3.push(`<!----> ${escape_html("저장")}</button></div></div> <div class="content-card svelte-famt8i"><div class="textarea-wrapper svelte-famt8i"><textarea placeholder="최종 체크 사항을 입력하세요..." class="textarea-field w-full svelte-famt8i">`);
      const $$body = escape_html(finalMessage);
      if ($$body) {
        $$renderer3.push(`${$$body}`);
      }
      $$renderer3.push(`</textarea></div> `);
      {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--></div></div> `);
      HelpModal($$renderer3, {
        title: "최종 메시지 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>📋 최종 메시지란?</h4> <p class="help-desc">AI가 응답을 생성하기 직전에 마지막으로 참고할 체크리스트입니다.
			응답의 품질, 형식, 톤 등을 검증하는 지침을 작성할 수 있습니다.</p></section> <section class="help-section"><h4>💡 Tip: 최종 메시지 활용법</h4> <div class="command-example"><code>응답 형식 검증</code> <p>태그 형식, 날짜 형식, 데이터 구조 등이 올바른지 확인하도록 지시합니다.
				예: "Check if all required tags are properly formatted"</p></div> <div class="command-example"><code>응답 톤 확인</code> <p>친근함, 격려, 전문성 등 응답의 톤이 적절한지 확인합니다.
				예: "Ensure the response is clear and professional"</p></div> <div class="command-example"><code>데이터 유효성 검사</code> <p>자율주행 관련 기술 정보, 계산 결과 등의 정확성을 검증합니다.
				예: "Verify technical accuracy of autonomous driving concepts"</p></div> <div class="command-example"><code>추가 지침</code> <p>참고 자료 제공, 예시 포함 등 추가적인 응답 개선 지침을 작성합니다.
				예: "Provide relevant references or examples when appropriate"</p></div></section> <section class="help-section"><h4>📝 기본 템플릿</h4> <p class="help-desc">초기화 버튼을 클릭하면 아래 기본 템플릿으로 복원됩니다.</p> <div class="example-box svelte-famt8i"><pre class="svelte-famt8i">## Final Checkout

- Check if all required tags are properly formatted
- Ensure the response is clear and professional
- Verify technical accuracy of autonomous driving concepts
- Provide relevant references or examples when appropriate</pre></div></section> <section class="help-section"><h4>🎯 사용 시나리오</h4> <div class="example-card svelte-famt8i"><h5 class="svelte-famt8i">자율주행 연구 프로젝트</h5> <p class="svelte-famt8i">"- Verify all SUMO XML tags are properly closed<br/> - Ensure vehicle parameters are within realistic ranges<br/> - Include simulation time estimates when relevant<br/> - Provide references to SUMO documentation"</p></div> <div class="example-card svelte-famt8i"><h5 class="svelte-famt8i">일반 AI 채팅</h5> <p class="svelte-famt8i">"- Use a friendly and encouraging tone<br/> - Break down complex concepts into simple steps<br/> - Provide actionable examples<br/> - End with a positive note"</p></div></section> <section class="help-section"><h4>⚠️ 주의사항</h4> <ul class="help-list"><li>너무 복잡한 체크리스트는 응답 생성 시간을 증가시킬 수 있습니다.</li> <li>명확하고 구체적인 지침을 작성하세요.</li> <li>최종 메시지는 모든 대화에 적용됩니다.</li></ul></section>`);
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
