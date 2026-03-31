import "clsx";
import { I as Icon } from "../../../../chunks/Icon.js";
import "@tauri-apps/api/core";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="page-container svelte-1e7qlye"><div class="page-header"><div><h1>캐릭터 관리</h1> <p class="page-description">AI 채팅 위젯에서 사용할 캐릭터를 관리합니다.</p></div> <button class="btn-primary">`);
    Icon($$renderer2, { icon: "solar:add-circle-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> 새 캐릭터</button></div> `);
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
