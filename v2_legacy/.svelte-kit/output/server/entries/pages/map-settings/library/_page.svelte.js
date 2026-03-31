import { Y as attr, X as ensure_array_like } from "../../../../chunks/index2.js";
import { o as onDestroy, I as Icon } from "../../../../chunks/Icon.js";
import "@tauri-apps/api/core";
import { D as Dialog } from "../../../../chunks/Dialog.js";
import "../../../../chunks/dbWatcher.svelte.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let maps = [];
    let categoryFilter = "all";
    let embeddedFilter = "all";
    let searchQuery = "";
    let filteredMaps = (() => {
      let result = maps;
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        result = result.filter((m) => m.name.toLowerCase().includes(query) || m.description.toLowerCase().includes(query));
      }
      return result;
    })();
    let buildingEmbeddings = false;
    let categories = (() => {
      const cats = new Set(maps.map((m) => m.category));
      return Array.from(cats).sort();
    })();
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="page-container svelte-1gvql8l"><div class="page-header"><div><h1>Map 라이브러리</h1> <p class="page-description">저장된 SUMO 맵을 조회하고 관리합니다.</p></div> <div class="header-actions"><button class="btn-secondary">`);
    Icon($$renderer2, { icon: "solar:map-point-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> 샘플맵 생성</button> <button class="btn-secondary"${attr("disabled", buildingEmbeddings, true)}>`);
    Icon($$renderer2, { icon: "solar:database-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> ${escape_html("전체 맵 Embed")}</button> <a href="/map-settings/generator" class="btn-primary">`);
    Icon($$renderer2, { icon: "solar:add-circle-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> 새 맵 생성</a></div></div> <div class="filters-section svelte-1gvql8l"><div class="filter-group svelte-1gvql8l">`);
    Icon($$renderer2, {
      icon: "solar:magnifer-bold-duotone",
      width: "20",
      height: "20"
    });
    $$renderer2.push(`<!----> <input type="text"${attr("value", searchQuery)} placeholder="맵 이름 또는 설명 검색..." class="search-input svelte-1gvql8l"/></div> <div class="filter-group svelte-1gvql8l">`);
    Icon($$renderer2, { icon: "solar:widget-5-bold", width: "20", height: "20" });
    $$renderer2.push(`<!----> `);
    $$renderer2.select(
      { value: categoryFilter, class: "filter-select" },
      ($$renderer3) => {
        $$renderer3.option({ value: "all" }, ($$renderer4) => {
          $$renderer4.push(`모든 카테고리`);
        });
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(categories);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let category = each_array[$$index];
          $$renderer3.option({ value: category }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(category)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      },
      "svelte-1gvql8l"
    );
    $$renderer2.push(`</div> <div class="filter-group svelte-1gvql8l">`);
    Icon($$renderer2, {
      icon: "solar:database-bold-duotone",
      width: "20",
      height: "20"
    });
    $$renderer2.push(`<!----> `);
    $$renderer2.select(
      { value: embeddedFilter, class: "filter-select" },
      ($$renderer3) => {
        $$renderer3.option({ value: "all" }, ($$renderer4) => {
          $$renderer4.push(`모든 상태`);
        });
        $$renderer3.option({ value: "embedded" }, ($$renderer4) => {
          $$renderer4.push(`임베딩 완료`);
        });
        $$renderer3.option({ value: "not_embedded" }, ($$renderer4) => {
          $$renderer4.push(`임베딩 대기`);
        });
      },
      "svelte-1gvql8l"
    );
    $$renderer2.push(`</div> <div class="stats-badge svelte-1gvql8l">`);
    Icon($$renderer2, { icon: "solar:map-point-bold", width: "16", height: "16" });
    $$renderer2.push(`<!----> <span>${escape_html(filteredMaps.length)}개 맵</span></div></div> <div class="content-section svelte-1gvql8l">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state">`);
      Icon($$renderer2, {
        icon: "solar:refresh-bold",
        width: "48",
        height: "48",
        class: "spin"
      });
      $$renderer2.push(`<!----> <p>맵 로딩 중...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    Dialog($$renderer2, {});
    $$renderer2.push(`<!---->`);
  });
}
export {
  _page as default
};
