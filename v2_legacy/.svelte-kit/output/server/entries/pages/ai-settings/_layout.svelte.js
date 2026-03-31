import { V as store_get, $ as attr_style, W as attr_class, X as ensure_array_like, Y as attr, Z as unsubscribe_stores } from "../../../chunks/index2.js";
import { p as page } from "../../../chunks/stores.js";
import { I as Icon } from "../../../chunks/Icon.js";
/* empty css                                                    */
import { e as escape_html } from "../../../chunks/escaping.js";
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { children } = $$props;
    let isCollapsed = false;
    const subMenus = [
      {
        path: "/ai-settings/chat-settings",
        icon: "solar:chat-round-dots-bold-duotone",
        label: "채팅 설정"
      },
      {
        path: "/ai-settings/system-messages",
        icon: "solar:document-text-bold-duotone",
        label: "시스템 메시지"
      },
      {
        path: "/ai-settings/characters",
        icon: "solar:user-bold-duotone",
        label: "캐릭터"
      },
      {
        path: "/ai-settings/commands",
        icon: "solar:code-bold-duotone",
        label: "명령어 템플릿"
      },
      {
        path: "/ai-settings/user-info",
        icon: "solar:users-group-rounded-bold-duotone",
        label: "유저 정보"
      },
      {
        path: "/ai-settings/final-message",
        icon: "solar:check-read-bold-duotone",
        label: "최종 메시지"
      }
    ];
    const currentPath = store_get($$store_subs ??= {}, "$page", page).url.pathname;
    $$renderer2.push(`<div class="sub-sidebar-layout"${attr_style("")}><aside${attr_class("sub-sidebar", void 0, { "collapsed": isCollapsed })}><div${attr_class("sub-sidebar-header", void 0, { "collapsed": isCollapsed })}>`);
    Icon($$renderer2, {
      icon: "solar:settings-bold-duotone",
      width: "24",
      height: "24"
    });
    $$renderer2.push(`<!----> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<h2>AI 설정</h2>`);
    }
    $$renderer2.push(`<!--]--></div> <nav class="sub-nav"><!--[-->`);
    const each_array = ensure_array_like(subMenus);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let menu = each_array[$$index];
      {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<a${attr("href", menu.path)}${attr_class("sub-nav-item", void 0, { "active": currentPath === menu.path })}>`);
        Icon($$renderer2, { icon: menu.icon, width: "20", height: "20" });
        $$renderer2.push(`<!----> <span>${escape_html(menu.label)}</span></a>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></nav> <div class="sub-sidebar-footer"><button class="sub-sidebar-toggle-btn">`);
    Icon($$renderer2, {
      icon: "solar:alt-arrow-left-bold-duotone",
      width: "24",
      height: "24"
    });
    $$renderer2.push(`<!----></button></div></aside> <main class="sub-content">`);
    children?.($$renderer2);
    $$renderer2.push(`<!----></main></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _layout as default
};
