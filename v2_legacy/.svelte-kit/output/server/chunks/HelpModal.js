import { a1 as slot, a2 as bind_props } from "./index2.js";
import { I as Icon } from "./Icon.js";
import { e as escape_html } from "./escaping.js";
function HelpModal($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { visible = void 0, title = "도움말", onClose } = $$props;
    if (visible) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="modal-backdrop svelte-apjqso" role="presentation"><div class="modal-container svelte-apjqso" role="dialog" aria-modal="true"><div class="modal-header svelte-apjqso"><h3 class="modal-title svelte-apjqso">`);
      Icon($$renderer2, { icon: "solar:book-bold-duotone", width: "24", height: "24" });
      $$renderer2.push(`<!----> ${escape_html(title)}</h3> <button class="btn-icon close-btn svelte-apjqso" title="닫기">`);
      Icon($$renderer2, { icon: "solar:close-circle-bold", width: "24", height: "24" });
      $$renderer2.push(`<!----></button></div> <div class="modal-content svelte-apjqso"><!--[-->`);
      slot($$renderer2, $$props, "default", {});
      $$renderer2.push(`<!--]--></div> <div class="modal-footer svelte-apjqso"><button class="btn-primary">닫기</button></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    bind_props($$props, { visible });
  });
}
export {
  HelpModal as H
};
