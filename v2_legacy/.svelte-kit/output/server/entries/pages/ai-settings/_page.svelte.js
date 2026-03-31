import "clsx";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import { I as Icon } from "../../../chunks/Icon.js";
import "@tauri-apps/api/core";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="settings-home svelte-h9jgab"><div class="page-header"><h1>AI 설정</h1> <p class="page-description">AI 채팅에 사용할 템플릿과 캐릭터를 선택하세요.</p></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state">`);
      Icon($$renderer2, { icon: "solar:ufo-2-duotone", width: "48", class: "spin" });
      $$renderer2.push(`<!----> <p>로딩 중...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
