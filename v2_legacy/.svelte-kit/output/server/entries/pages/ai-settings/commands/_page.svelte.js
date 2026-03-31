import { X as ensure_array_like, W as attr_class } from "../../../../chunks/index2.js";
import { o as onDestroy, I as Icon } from "../../../../chunks/Icon.js";
import "@tauri-apps/api/core";
import "../../../../chunks/dbWatcher.svelte.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let templates = [];
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="page-container svelte-xkk810"><div class="page-header svelte-xkk810"><div><h1>명령어 템플릿</h1> <p class="page-description">AI에게 전달할 명령어 정보를 관리합니다. 활성화된 템플릿만 전송됩니다.</p></div> <button class="btn-primary">`);
    Icon($$renderer2, {
      icon: "solar:add-circle-bold-duotone",
      width: "20",
      height: "20"
    });
    $$renderer2.push(`<!----> <span>새 템플릿</span></button></div> `);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[!-->");
        if (templates.length === 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="empty-state">`);
          Icon($$renderer2, {
            icon: "solar:document-bold-duotone",
            width: "64",
            class: "empty-state-icon"
          });
          $$renderer2.push(`<!----> <p>등록된 명령어 템플릿이 없습니다.</p> <button class="btn-secondary">템플릿 추가하기</button></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="templates-list svelte-xkk810"><!--[-->`);
          const each_array = ensure_array_like(templates);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let template = each_array[$$index];
            $$renderer2.push(`<div${attr_class("template-card svelte-xkk810", void 0, { "inactive": template.isActive === 0 })}><div class="template-header svelte-xkk810"><div class="template-title svelte-xkk810"><h3 class="svelte-xkk810">${escape_html(template.name)}</h3> <span${attr_class("badge", void 0, {
              "badge-success": template.isActive === 1,
              "badge-neutral": template.isActive === 0
            })}>${escape_html(template.isActive === 1 ? "활성화" : "비활성화")}</span></div> <div class="template-actions svelte-xkk810"><button class="btn-icon" title="활성화 토글">`);
            Icon($$renderer2, {
              icon: template.isActive === 1 ? "solar:eye-bold-duotone" : "solar:eye-closed-bold-duotone",
              width: "20",
              height: "20"
            });
            $$renderer2.push(`<!----></button> <button class="btn-icon" title="수정">`);
            Icon($$renderer2, { icon: "solar:pen-bold-duotone", width: "20", height: "20" });
            $$renderer2.push(`<!----></button> <button class="btn-icon danger" title="삭제">`);
            Icon($$renderer2, {
              icon: "solar:trash-bin-trash-bold-duotone",
              width: "20",
              height: "20"
            });
            $$renderer2.push(`<!----></button></div></div> <div class="template-content svelte-xkk810"><pre class="svelte-xkk810">${escape_html(template.content)}</pre></div> <div class="template-footer svelte-xkk810"><span class="date">생성: ${escape_html(new Date(template.created_at).toLocaleString("ko-KR"))}</span> <span class="date">수정: ${escape_html(new Date(template.updated_at).toLocaleString("ko-KR"))}</span></div></div>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _page as default
};
