import "clsx";
import "../../../chunks/settingsStore.js";
import "@tauri-apps/api/core";
import "@tauri-apps/plugin-dialog";
import { I as Icon } from "../../../chunks/Icon.js";
import { H as HelpModal } from "../../../chunks/HelpModal.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let showHelpModal = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="app-settings svelte-1kw50c4"><div class="page-header"><div><div class="title-row svelte-1kw50c4"><h1>앱 설정</h1> <button class="btn-icon help-btn">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></div> <p class="page-description">데이터베이스, 백업 및 Claude 작업 디렉토리를 관리합니다.</p></div></div> `);
      {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<div class="loading-state"><p class="text-muted">설정 로딩 중...</p></div>`);
      }
      $$renderer3.push(`<!--]--></div> `);
      HelpModal($$renderer3, {
        title: "앱 설정 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>💡 설정 안내</h4> <ul class="help-list"><li><strong>데이터베이스 경로</strong>: 원드라이브 등 클라우드 경로를 지정하면 여러 PC에서 동기화됩니다.</li> <li><strong>백업</strong>: 앱 종료 시 자동 백업 (타임스탬프 파일명, 최근 10개 유지).</li> <li><strong>기본 DB/백업 위치</strong>: <code>AppData\\Roaming\\AGI_VOICE\\ai_chat.db</code> / <code>AppData\\Roaming\\AGI_VOICE\\backups\\</code></li> <li><strong>Claude 실행 폴더</strong>: AI 채팅 시 Claude CLI가 실행될 작업 디렉토리입니다.</li> <li>비어있으면 기본값(<code>AppData\\Roaming\\AGI_VOICE</code>)을 사용합니다.</li> <li>폴더가 존재하지 않으면 저장 시 오류가 발생합니다.</li> <li>설정은 <code>AppData\\Roaming\\AGI_VOICE\\config.json</code>에 저장됩니다.</li></ul></section> <section class="help-section"><h4>📊 DB 정보</h4> <p class="help-desc">현재 사용 중인 데이터베이스의 정보를 확인할 수 있습니다.
      위치, 크기, 마지막 수정 시간 등을 표시합니다.</p></section> <section class="help-section"><h4>💾 백업 관리</h4> <p class="help-desc">최근 10개의 백업 파일 목록을 확인하고 복원할 수 있습니다.
      각 백업은 타임스탬프 파일명으로 저장되며, 복원 버튼을 통해 이전 상태로 되돌릴 수 있습니다.</p></section> <section class="help-section"><h4>🔄 수동 동기화</h4> <p class="help-desc">데이터베이스 경로가 설정된 경우, 수동 동기화 버튼으로 즉시 동기화할 수 있습니다.
      일반적으로 앱 시작/종료 시 자동 동기화되지만, 필요시 수동으로 실행할 수 있습니다.</p></section>`);
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
