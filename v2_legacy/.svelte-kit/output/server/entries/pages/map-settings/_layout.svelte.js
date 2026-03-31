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
        path: "/map-settings/generator",
        icon: "solar:map-bold-duotone",
        label: "Map 생성"
      },
      {
        path: "/map-settings/library",
        icon: "solar:folder-with-files-bold-duotone",
        label: "Map 라이브러리"
      },
      {
        path: "/map-settings/rag-test",
        icon: "solar:magnifer-zoom-in-bold-duotone",
        label: "RAG 테스트"
      }
    ];
    const currentPath = store_get($$store_subs ??= {}, "$page", page).url.pathname;
    $$renderer2.push(`<div class="sub-sidebar-layout"${attr_style("")}><aside${attr_class("sub-sidebar", void 0, { "collapsed": isCollapsed })}><div${attr_class("sub-sidebar-header", void 0, { "collapsed": isCollapsed })}>`);
    Icon($$renderer2, {
      icon: "solar:map-point-wave-bold-duotone",
      width: "24",
      height: "24"
    });
    $$renderer2.push(`<!----> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<h2>Map 설정</h2>`);
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
