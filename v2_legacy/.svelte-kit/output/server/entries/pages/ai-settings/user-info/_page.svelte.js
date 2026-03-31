import { Y as attr } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let userName = "";
    let userInfo = "";
    let isSaving = false;
    let showHelpModal = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="page-container svelte-lok5b6"><div class="page-header"><div><div class="title-row svelte-lok5b6"><h1>유저 정보</h1> <button class="btn-icon help-btn">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></div> <p class="page-description">AI가 참고할 사용자 정보를 입력하세요.</p></div> <button class="btn-primary"${attr("disabled", isSaving, true)}>`);
      Icon($$renderer3, { icon: "solar:diskette-bold", width: "20", height: "20" });
      $$renderer3.push(`<!----> ${escape_html("저장")}</button></div> <div class="content-card svelte-lok5b6"><div class="input-section svelte-lok5b6"><label for="userName" class="form-label">`);
      Icon($$renderer3, { icon: "solar:user-bold-duotone", width: "20", height: "20" });
      $$renderer3.push(`<!----> 사용자 이름</label> <input id="userName" type="text"${attr("value", userName)} placeholder="예: 홍길동" class="input-field"/> <p class="input-hint svelte-lok5b6">프롬프트에서 <code class="svelte-lok5b6">{{user}}</code>로 사용됩니다.</p></div> <div class="textarea-wrapper svelte-lok5b6"><label for="userInfo" class="form-label">`);
      Icon($$renderer3, {
        icon: "solar:document-text-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----> 사용자 정보</label> <textarea id="userInfo" placeholder="예: - 연구 분야: 자율주행 시스템 개발 - 관심 주제: SLAM, 경로 계획, 센서 퓨전 - 사용 센서: LiDAR, 카메라, IMU - 개발 환경: ROS2, Python, C++ - 목표: 실시간 맵 생성 및 주행 판단 알고리즘 최적화  자유롭게 작성하세요..." class="textarea-field w-full">`);
      const $$body = escape_html(userInfo);
      if ($$body) {
        $$renderer3.push(`${$$body}`);
      }
      $$renderer3.push(`</textarea></div> `);
      {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--></div></div> `);
      HelpModal($$renderer3, {
        title: "변수 치환 시스템 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>🔄 변수 치환 시스템이란?</h4> <p class="help-desc">프롬프트에서 특정 변수를 사용하면 실제 대화 시 자동으로 실제 값으로 치환됩니다.
			이를 통해 동적이고 개인화된 AI 대화를 구성할 수 있습니다.</p></section> <section class="help-section"><h4>📋 사용 가능한 변수</h4> <div class="command-example"><code>{{user}}</code> <p>사용자 이름으로 대체됩니다.
				예: "홍길동" 입력 시 → "Hello {{user}}!" → "Hello 홍길동!"</p></div> <div class="command-example"><code>{{char}}</code> <p>선택된 캐릭터 이름으로 대체됩니다.
				예: "Research Assistant" 선택 시 → "Respond as {{char}}" → "Respond as Research Assistant"</p></div></section> <section class="help-section"><h4>💡 사용 예시</h4> <div class="example-card svelte-lok5b6"><h5 class="svelte-lok5b6">시스템 메시지에서 사용</h5> <p class="svelte-lok5b6">"You are in a text messaging conversation with <code>{{user}}</code>.
				Respond as <code>{{char}}</code> would, using a friendly and encouraging tone."</p></div> <div class="example-card svelte-lok5b6"><h5 class="svelte-lok5b6">실제 치환 결과</h5> <p class="svelte-lok5b6">사용자: "홍길동", 캐릭터: "Research Assistant" 선택 시<br/> → "You are in a text messaging conversation with <strong>홍길동</strong>.
				Respond as <strong>Research Assistant</strong> would, using a professional and friendly tone."</p></div></section> <section class="help-section"><h4>🎯 변수 사용 위치</h4> <ul class="help-list"><li><strong>시스템 메시지</strong>: AI의 역할과 행동 정의</li> <li><strong>캐릭터 프롬프트</strong>: 캐릭터 성격과 말투 정의</li> <li><strong>명령어 템플릿</strong>: 명령어 실행 시 참고 정보</li></ul></section> <section class="help-section"><h4>📝 사용자 정보 활용</h4> <p class="help-desc"><strong>사용자 정보</strong> 필드는 변수로 치환되지 않지만,
			프롬프트 시스템에 포함되어 AI가 사용자의 맥락을 이해하는 데 도움을 줍니다.</p> <ul class="help-list"><li>연구 분야, 관심사, 사용 환경 등을 입력</li> <li>AI가 더 맞춤화된 답변 제공</li> <li>대화 품질 향상</li></ul></section>`);
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
