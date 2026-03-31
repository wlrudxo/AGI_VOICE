import { a2 as bind_props } from "./index2.js";
import { e as escape_html } from "./escaping.js";
function Dialog($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let visible = false;
    let dialogType = "alert";
    let title = "";
    let message = "";
    function confirm(msg, titleText = "확인") {
      return new Promise((resolve) => {
        dialogType = "confirm";
        title = titleText;
        message = msg;
        visible = true;
      });
    }
    function alert(msg, titleText = "알림") {
      return new Promise((resolve) => {
        dialogType = "alert";
        title = titleText;
        message = msg;
        visible = true;
      });
    }
    if (visible) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="dialog-backdrop svelte-jby388" role="presentation"><div class="dialog-container svelte-jby388" role="dialog" aria-labelledby="dialog-title" aria-modal="true"><div class="dialog-header svelte-jby388"><h3 id="dialog-title" class="dialog-title svelte-jby388">${escape_html(title)}</h3></div> <div class="dialog-content svelte-jby388"><p class="dialog-message svelte-jby388">${escape_html(message)}</p></div> <div class="dialog-footer svelte-jby388">`);
      if (dialogType === "confirm") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button class="btn-secondary svelte-jby388">취소</button> <button class="btn-primary svelte-jby388">확인</button>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<button class="btn-primary svelte-jby388">확인</button>`);
      }
      $$renderer2.push(`<!--]--></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    bind_props($$props, { confirm, alert });
  });
}
export {
  Dialog as D
};
