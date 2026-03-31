import { Y as attr, X as ensure_array_like } from "../../../../chunks/index2.js";
import "@tauri-apps/api/core";
import { I as Icon } from "../../../../chunks/Icon.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let query = "";
    let topK = 5;
    let results = [];
    let loading = false;
    $$renderer2.push(`<div class="page-container svelte-3rjejz"><div class="page-header"><div><h1>RAG 테스트</h1> <p class="page-description">자연어 검색으로 유사한 맵을 찾습니다.</p></div></div> <div class="search-section svelte-3rjejz"><div class="search-input-group svelte-3rjejz">`);
    Icon($$renderer2, {
      icon: "solar:magnifer-bold-duotone",
      width: "24",
      height: "24"
    });
    $$renderer2.push(`<!----> <input type="text"${attr("value", query)} placeholder="예: 교차로가 있는 복잡한 도로" class="search-input svelte-3rjejz"${attr("disabled", loading, true)}/> <button class="btn-primary"${attr("disabled", !query.trim(), true)}>`);
    {
      $$renderer2.push("<!--[!-->");
      Icon($$renderer2, { icon: "solar:magnifer-bold", width: "20", height: "20" });
      $$renderer2.push(`<!----> 검색`);
    }
    $$renderer2.push(`<!--]--></button></div> <div class="search-options svelte-3rjejz"><label class="svelte-3rjejz"><span>상위 결과 개수:</span> <input type="number"${attr("value", topK)} min="1" max="20" class="number-input svelte-3rjejz"${attr("disabled", loading, true)}/></label></div></div> <div class="results-section svelte-3rjejz">`);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[!-->");
        if (results.length === 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="empty-state">`);
          Icon($$renderer2, {
            icon: "solar:magnifer-zoom-in-bold-duotone",
            width: "64",
            height: "64"
          });
          $$renderer2.push(`<!----> <h3>검색 결과가 없습니다</h3> <p>검색어를 입력하고 검색 버튼을 눌러주세요.</p></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="results-header svelte-3rjejz"><h3 class="svelte-3rjejz">${escape_html(results.length)}개의 유사한 맵을 찾았습니다</h3></div> <div class="results-list svelte-3rjejz"><!--[-->`);
          const each_array = ensure_array_like(results);
          for (let index = 0, $$length = each_array.length; index < $$length; index++) {
            let result = each_array[index];
            $$renderer2.push(`<div class="result-card svelte-3rjejz"><div class="result-rank svelte-3rjejz">#${escape_html(index + 1)}</div> <div class="result-content svelte-3rjejz"><div class="result-header svelte-3rjejz"><h4 class="svelte-3rjejz">${escape_html(result.mapName)}</h4> <div class="result-badges svelte-3rjejz"><span class="badge category svelte-3rjejz">${escape_html(result.category)}</span> <span class="badge difficulty svelte-3rjejz">${escape_html(result.difficulty)}</span></div></div> <p class="result-description svelte-3rjejz">${escape_html(result.description)}</p> `);
            if (result.tags && result.tags.length > 0) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="result-tags svelte-3rjejz"><!--[-->`);
              const each_array_1 = ensure_array_like(result.tags);
              for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
                let tag = each_array_1[$$index];
                $$renderer2.push(`<span class="tag svelte-3rjejz">${escape_html(tag)}</span>`);
              }
              $$renderer2.push(`<!--]--></div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> <div class="result-footer svelte-3rjejz"><div class="score-info svelte-3rjejz">`);
            Icon($$renderer2, { icon: "solar:star-bold", width: "16", height: "16" });
            $$renderer2.push(`<!----> <span>유사도: ${escape_html((result.similarityScore * 100).toFixed(1))}%</span></div> <div class="distance-info svelte-3rjejz">`);
            Icon($$renderer2, { icon: "solar:target-bold", width: "16", height: "16" });
            $$renderer2.push(`<!----> <span>거리: ${escape_html(result.distance.toFixed(4))}</span></div> <div class="embedding-status svelte-3rjejz">`);
            if (result.isEmbedded) {
              $$renderer2.push("<!--[-->");
              Icon($$renderer2, {
                icon: "solar:check-circle-bold",
                width: "16",
                height: "16",
                class: "embedded"
              });
              $$renderer2.push(`<!----> <span class="embedded svelte-3rjejz">임베딩 완료</span>`);
            } else {
              $$renderer2.push("<!--[!-->");
              Icon($$renderer2, {
                icon: "solar:close-circle-bold",
                width: "16",
                height: "16",
                class: "not-embedded"
              });
              $$renderer2.push(`<!----> <span class="not-embedded svelte-3rjejz">임베딩 대기</span>`);
            }
            $$renderer2.push(`<!--]--></div></div></div></div>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
export {
  _page as default
};
