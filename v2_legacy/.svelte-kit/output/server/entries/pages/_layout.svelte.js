import { V as store_get, W as attr_class, X as ensure_array_like, Y as attr, Z as unsubscribe_stores, _ as stringify, $ as attr_style } from "../../chunks/index2.js";
import "clsx";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { I as Icon, h as html } from "../../chunks/Icon.js";
import { w as writable } from "../../chunks/index.js";
import { p as page } from "../../chunks/stores.js";
/* empty css                                                 */
import { e as escape_html } from "../../chunks/escaping.js";
import { t as triggerMonitor } from "../../chunks/triggerMonitor.svelte.js";
import "@tauri-apps/api/core";
import "../../chunks/dbWatcher.svelte.js";
import { marked } from "marked";
import { D as Dialog } from "../../chunks/Dialog.js";
import { t as toastStore } from "../../chunks/carmakerStore.svelte.js";
import "../../chunks/settingsStore.js";
import "@tauri-apps/plugin-global-shortcut";
function loadInitialState() {
  if (typeof window === "undefined") {
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: "chat",
      currentConversationId: null,
      currentConversationTitle: null,
      isWidgetMode: false,
      wasWidgetModeBeforeTray: false,
      isChatExpanded: false
    };
  }
  try {
    const storedViewMode = localStorage.getItem("agi_voice_chat_view_mode");
    const storedConversationId = localStorage.getItem("agi_voice_conversation_id");
    const storedWasWidgetMode = localStorage.getItem("agi_voice_was_widget_mode_before_tray");
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: storedViewMode === "history" ? "history" : storedViewMode === "settings" ? "settings" : "chat",
      currentConversationId: storedConversationId ? parseInt(storedConversationId, 10) : null,
      currentConversationTitle: null,
      isWidgetMode: false,
      wasWidgetModeBeforeTray: storedWasWidgetMode === "true",
      isChatExpanded: false
    };
  } catch (error) {
    console.error("Failed to load initial state:", error);
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: "chat",
      currentConversationId: null,
      currentConversationTitle: null,
      isWidgetMode: false,
      wasWidgetModeBeforeTray: false,
      isChatExpanded: false
    };
  }
}
function createUiStore() {
  const { subscribe, set, update } = writable(loadInitialState());
  return {
    subscribe,
    toggleSidebar: () => update((state) => ({
      ...state,
      isSidebarCollapsed: !state.isSidebarCollapsed
    })),
    setSidebarCollapsed: (collapsed) => update((state) => ({
      ...state,
      isSidebarCollapsed: collapsed
    })),
    toggleChat: () => update((state) => ({
      ...state,
      isChatOpen: !state.isChatOpen
    })),
    setChatOpen: (open) => update((state) => ({
      ...state,
      isChatOpen: open
    })),
    setChatViewMode: (mode) => {
      update((state) => ({
        ...state,
        chatViewMode: mode
      }));
      if (typeof window !== "undefined") {
        try {
          localStorage.setItem("agi_voice_chat_view_mode", mode);
        } catch (error) {
          console.error("Failed to save chat view mode:", error);
        }
      }
    },
    setCurrentConversationId: (id) => {
      update((state) => ({
        ...state,
        currentConversationId: id
      }));
      if (typeof window !== "undefined") {
        try {
          if (id === null) {
            localStorage.removeItem("agi_voice_conversation_id");
          } else {
            localStorage.setItem("agi_voice_conversation_id", id.toString());
          }
        } catch (error) {
          console.error("Failed to save conversation id:", error);
        }
      }
    },
    setCurrentConversationTitle: (title) => {
      update((state) => ({
        ...state,
        currentConversationTitle: title
      }));
    },
    setWidgetMode: (isWidgetMode) => {
      update((state) => ({
        ...state,
        isWidgetMode,
        isChatOpen: isWidgetMode ? true : state.isChatOpen
      }));
    },
    saveWidgetModeBeforeTray: (wasWidgetMode) => {
      update((state) => ({
        ...state,
        wasWidgetModeBeforeTray: wasWidgetMode
      }));
      if (typeof window !== "undefined") {
        try {
          localStorage.setItem("agi_voice_was_widget_mode_before_tray", wasWidgetMode.toString());
        } catch (error) {
          console.error("Failed to save widget mode before tray:", error);
        }
      }
    },
    restoreModeFromTray: () => {
      update((state) => {
        const shouldBeWidgetMode = state.wasWidgetModeBeforeTray;
        return {
          ...state,
          isWidgetMode: shouldBeWidgetMode,
          isChatOpen: shouldBeWidgetMode ? true : state.isChatOpen
        };
      });
    },
    setChatExpanded: (isExpanded) => update((state) => ({
      ...state,
      isChatExpanded: isExpanded
    }))
  };
}
const uiStore = createUiStore();
function TitleBar($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    getCurrentWindow();
    $$renderer2.push(`<div class="titlebar svelte-tq03kl" data-tauri-drag-region=""><div class="titlebar-left svelte-tq03kl" data-tauri-drag-region=""><span class="app-title svelte-tq03kl" data-tauri-drag-region="">AGI Voice</span></div> <div class="titlebar-right svelte-tq03kl"><button class="titlebar-button svelte-tq03kl" title="위젯 모드">`);
    Icon($$renderer2, {
      icon: "solar:widget-5-bold-duotone",
      width: "18",
      height: "18"
    });
    $$renderer2.push(`<!----></button> <button class="titlebar-button svelte-tq03kl" title="최소화">`);
    Icon($$renderer2, { icon: "solar:minus-square-linear", width: "18", height: "18" });
    $$renderer2.push(`<!----></button> <button class="titlebar-button svelte-tq03kl" title="최대화">`);
    Icon($$renderer2, { icon: "solar:stop-bold-duotone", width: "18", height: "18" });
    $$renderer2.push(`<!----></button> <button class="titlebar-button close svelte-tq03kl" title="닫기">`);
    Icon($$renderer2, { icon: "solar:close-square-linear", width: "18", height: "18" });
    $$renderer2.push(`<!----></button></div></div>`);
  });
}
function Tooltip($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { text = "", position = "right", children } = $$props;
    $$renderer2.push(`<div class="tooltip-wrapper svelte-11extwn" role="tooltip">`);
    children?.($$renderer2);
    $$renderer2.push(`<!----></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function Sidebar($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let currentPath, collapsed, isChatOpen;
    const navItems = [
      { name: "대시보드", path: "/", icon: "solar:widget-2-bold-duotone" },
      {
        name: "자율주행",
        path: "/autonomous-driving",
        icon: "solar:wheel-bold-duotone"
      },
      {
        name: "Map 생성",
        path: "/map-settings",
        icon: "solar:map-point-wave-bold-duotone"
      },
      {
        name: "AI 설정",
        path: "/ai-settings",
        icon: "solar:settings-minimalistic-bold-duotone"
      },
      {
        name: "앱 설정",
        path: "/app-settings",
        icon: "solar:settings-bold-duotone"
      }
    ];
    function isActive(itemPath) {
      if (itemPath === "/") {
        return currentPath === "/";
      }
      return currentPath.startsWith(itemPath);
    }
    currentPath = store_get($$store_subs ??= {}, "$page", page).url.pathname;
    collapsed = store_get($$store_subs ??= {}, "$uiStore", uiStore).isSidebarCollapsed;
    isChatOpen = store_get($$store_subs ??= {}, "$uiStore", uiStore).isChatOpen;
    $$renderer2.push(`<aside${attr_class("sidebar bg-sidebar svelte-129hoe0", void 0, { "collapsed": collapsed })}><nav class="nav-section svelte-129hoe0"><!--[-->`);
    const each_array = ensure_array_like(navItems);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let item = each_array[$$index];
      if (collapsed) {
        $$renderer2.push("<!--[-->");
        Tooltip($$renderer2, {
          text: item.name,
          position: "right",
          children: ($$renderer3) => {
            $$renderer3.push(`<a${attr("href", item.path)}${attr_class("nav-item svelte-129hoe0", void 0, { "active": isActive(item.path), "collapsed": collapsed })}>`);
            Icon($$renderer3, { icon: item.icon, width: "24", height: "24" });
            $$renderer3.push(`<!----></a>`);
          }
        });
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<a${attr("href", item.path)}${attr_class("nav-item svelte-129hoe0", void 0, { "active": isActive(item.path) })}>`);
        Icon($$renderer2, { icon: item.icon, width: "24", height: "24" });
        $$renderer2.push(`<!----> <span class="nav-label svelte-129hoe0">${escape_html(item.name)}</span></a>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></nav> <div class="chat-buttons-section svelte-129hoe0">`);
    if (collapsed) {
      $$renderer2.push("<!--[-->");
      Tooltip($$renderer2, {
        text: "AI 채팅",
        position: "right",
        children: ($$renderer3) => {
          $$renderer3.push(`<button${attr_class("chat-toggle-btn svelte-129hoe0", void 0, { "active": isChatOpen })}>`);
          Icon($$renderer3, {
            icon: "solar:chat-round-dots-bold-duotone",
            width: "24",
            height: "24"
          });
          $$renderer3.push(`<!----></button>`);
        }
      });
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<button${attr_class("chat-toggle-btn svelte-129hoe0", void 0, { "active": isChatOpen })}>`);
      Icon($$renderer2, {
        icon: "solar:chat-round-dots-bold-duotone",
        width: "24",
        height: "24"
      });
      $$renderer2.push(`<!----> <span class="chat-label svelte-129hoe0">AI 채팅</span></button>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="toggle-section svelte-129hoe0"><button class="toggle-btn svelte-129hoe0">`);
    Icon($$renderer2, {
      icon: collapsed ? "solar:alt-arrow-right-bold-duotone" : "solar:alt-arrow-left-bold-duotone",
      width: "24",
      height: "24"
    });
    $$renderer2.push(`<!----></button></div></aside>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ChatView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    marked.setOptions({
      breaks: true,
      // Convert \n to <br>
      gfm: true
      // GitHub Flavored Markdown
    });
    function preprocessMarkdown(content) {
      const parts = [];
      let inCodeBlock = false;
      let inInlineCode = false;
      let currentPart = "";
      for (let i = 0; i < content.length; i++) {
        const char = content[i];
        const nextChars = content.slice(i, i + 3);
        if (nextChars === "```") {
          parts.push(currentPart);
          currentPart = "```";
          inCodeBlock = !inCodeBlock;
          i += 2;
          continue;
        }
        if (char === "`" && !inCodeBlock) {
          parts.push(currentPart);
          currentPart = "`";
          inInlineCode = !inInlineCode;
          continue;
        }
        if (!inCodeBlock && !inInlineCode) {
          if (char === "<") {
            currentPart += "&lt;";
            continue;
          }
          if (char === ">") {
            currentPart += "&gt;";
            continue;
          }
        }
        currentPart += char;
      }
      parts.push(currentPart);
      return parts.join("");
    }
    let messages = [];
    let inputMessage = "";
    let isLoading = false;
    let collapsedVehicleData = {};
    function parseSystemMessage(content) {
      const vehicleDataMatch = content.match(/## Current Vehicle Data:\n([\s\S]*?)(?=\n##|$)/);
      if (vehicleDataMatch) {
        const vehicleData = vehicleDataMatch[1].trim();
        const vehicleDataCount = vehicleData.split("\n").filter((line) => line.trim()).length;
        const otherContent = content.replace(/## Current Vehicle Data:\n[\s\S]*?(?=\n##|$)/, "").trim();
        return { vehicleData, vehicleDataCount, otherContent };
      }
      return {
        vehicleData: null,
        vehicleDataCount: 0,
        otherContent: content
      };
    }
    function formatTime(date) {
      const hours = date.getHours().toString().padStart(2, "0");
      const minutes = date.getMinutes().toString().padStart(2, "0");
      return `${hours}:${minutes}`;
    }
    function shouldShowTime(index) {
      if (index === messages.length - 1) return true;
      const currentRole = messages[index].role;
      const nextRole = messages[index + 1]?.role;
      return currentRole !== nextRole;
    }
    $$renderer2.push(`<div class="chat-view svelte-may7r9"><div class="messages-container svelte-may7r9">`);
    if (messages.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="empty-state svelte-may7r9"></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(messages);
      for (let index = 0, $$length = each_array.length; index < $$length; index++) {
        let message = each_array[index];
        if (message.role === "user") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="message-wrapper message-wrapper-user svelte-may7r9">`);
          if (shouldShowTime(index)) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="message-time message-time-user svelte-may7r9">${escape_html(formatTime(message.timestamp))}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <div class="message message-user svelte-may7r9"><div class="message-content svelte-may7r9"><p class="svelte-may7r9">${escape_html(message.content)}</p></div></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.role === "system") {
          $$renderer2.push("<!--[-->");
          const parsed = parseSystemMessage(message.content);
          $$renderer2.push(`<div class="message message-system svelte-may7r9"><div class="message-content svelte-may7r9"><div class="system-indicator svelte-may7r9">`);
          Icon($$renderer2, { icon: "solar:info-circle-bold-duotone", width: "16" });
          $$renderer2.push(`<!----> <span class="svelte-may7r9">시스템</span></div> `);
          if (parsed.vehicleData) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="vehicle-data-toggle svelte-may7r9">`);
            Icon($$renderer2, {
              icon: collapsedVehicleData[index] === false ? "solar:alt-arrow-down-bold" : "solar:alt-arrow-right-bold",
              width: "14"
            });
            $$renderer2.push(`<!----> <span class="svelte-may7r9">Vehicle Data (${escape_html(parsed.vehicleDataCount)}개 항목)</span></button> `);
            if (collapsedVehicleData[index] === false) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<pre class="vehicle-data-content svelte-may7r9">${escape_html(parsed.vehicleData)}</pre>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> <div class="markdown-content system-other-content svelte-may7r9">${html(marked(parsed.otherContent))}</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<p class="svelte-may7r9">${escape_html(message.content)}</p>`);
          }
          $$renderer2.push(`<!--]--></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.role === "action") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="message message-action svelte-may7r9"><div class="message-content svelte-may7r9"><div class="action-indicator svelte-may7r9">${escape_html(message.label)}</div></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.role === "assistant") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="message-wrapper message-wrapper-assistant svelte-may7r9"><div class="message message-assistant svelte-may7r9"><div class="message-content svelte-may7r9"><div class="markdown-content svelte-may7r9">${html(marked(preprocessMarkdown(message.content)))}</div></div></div> `);
          if (shouldShowTime(index)) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="message-time message-time-assistant svelte-may7r9">${escape_html(formatTime(message.timestamp))}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.role === "error") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="message-wrapper message-wrapper-user svelte-may7r9">`);
          if (shouldShowTime(index)) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="message-time message-time-user svelte-may7r9">${escape_html(formatTime(message.timestamp))}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <div class="message message-error svelte-may7r9"><div class="message-content svelte-may7r9"><p class="svelte-may7r9">${escape_html(message.content)}</p></div></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--> `);
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> <div class="input-container svelte-may7r9"><input type="text"${attr("value", inputMessage)} placeholder="메시지를 입력하세요..."${attr("disabled", isLoading, true)} class="svelte-may7r9"/> <button class="btn-primary svelte-may7r9"${attr("disabled", !inputMessage.trim() || isLoading, true)}>`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`전송`);
    }
    $$renderer2.push(`<!--]--></button></div></div>`);
  });
}
function ChatHistoryView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let conversations = [];
    let editingId = null;
    let editingTitle = "";
    function formatDate(dateStr) {
      const dbDate = new Date(dateStr);
      const now = /* @__PURE__ */ new Date();
      const diff = now - dbDate;
      const minutes = Math.floor(diff / 6e4);
      const hours = Math.floor(diff / 36e5);
      const days = Math.floor(diff / 864e5);
      if (minutes < 1) {
        return "방금 전";
      } else if (minutes < 60) {
        return `${minutes}분 전`;
      } else if (hours < 24) {
        return `${hours}시간 전`;
      } else if (days < 7) {
        return `${days}일 전`;
      } else {
        return dbDate.toLocaleDateString("ko-KR", { timeZone: "Asia/Seoul" });
      }
    }
    $$renderer2.push(`<div class="history-view svelte-1l3p8yv"><div class="history-container svelte-1l3p8yv">`);
    {
      $$renderer2.push("<!--[!-->");
      if (conversations.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="empty-state svelte-1l3p8yv">`);
        Icon($$renderer2, {
          icon: "solar:chat-line-bold-duotone",
          width: "64",
          height: "64"
        });
        $$renderer2.push(`<!----> <p>저장된 대화가 없습니다</p> <p class="hint svelte-1l3p8yv">AI 채팅을 시작해보세요!</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="conversation-list svelte-1l3p8yv"><!--[-->`);
        const each_array = ensure_array_like(conversations);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let conversation = each_array[$$index];
          $$renderer2.push(`<div class="conversation-item svelte-1l3p8yv">`);
          if (editingId === conversation.id) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="edit-mode svelte-1l3p8yv"><input type="text"${attr("value", editingTitle)} class="edit-input svelte-1l3p8yv"/> <div class="edit-actions svelte-1l3p8yv"><button class="btn-icon">`);
            Icon($$renderer2, { icon: "solar:check-circle-bold", width: "20", height: "20" });
            $$renderer2.push(`<!----></button> <button class="btn-icon danger">`);
            Icon($$renderer2, { icon: "solar:close-circle-bold", width: "20", height: "20" });
            $$renderer2.push(`<!----></button></div></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<button class="conversation-content svelte-1l3p8yv"><div class="conversation-title svelte-1l3p8yv">${escape_html(conversation.title || "제목 없음")}</div> <div class="conversation-meta svelte-1l3p8yv"><span class="conversation-date">${escape_html(formatDate(conversation.createdAt))}</span> <span class="conversation-separator">•</span> <span class="conversation-messages">메시지 ${escape_html(conversation.messageCount || 0)}개</span></div></button> <div class="conversation-actions svelte-1l3p8yv"><button class="btn-icon">`);
            Icon($$renderer2, { icon: "solar:pen-bold-duotone", width: "18", height: "18" });
            $$renderer2.push(`<!----></button> <button class="btn-icon danger">`);
            Icon($$renderer2, {
              icon: "solar:trash-bin-trash-bold-duotone",
              width: "18",
              height: "18"
            });
            $$renderer2.push(`<!----></button></div>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
function ChatSettingsView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="chat-settings-view svelte-1nyecta">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state svelte-1nyecta"><p>설정 로딩 중...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function AIChatWidget($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    getCurrentWindow();
    let viewMode = store_get($$store_subs ??= {}, "$uiStore", uiStore).chatViewMode;
    let currentTitle = store_get($$store_subs ??= {}, "$uiStore", uiStore).currentConversationTitle;
    let isWidgetMode = store_get($$store_subs ??= {}, "$uiStore", uiStore).isWidgetMode;
    let isExpanded = store_get($$store_subs ??= {}, "$uiStore", uiStore).isChatExpanded;
    let isTriggerMonitoring = triggerMonitor.isMonitoring;
    $$renderer2.push(`<div${attr_class("chat-widget svelte-rtvhgo", void 0, { "fullscreen-widget": isWidgetMode, "expanded": isExpanded })}><div class="chat-header svelte-rtvhgo"><div class="header-title svelte-rtvhgo">`);
    if (viewMode === "chat") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="title-text svelte-rtvhgo">${escape_html(currentTitle || "새 채팅")}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (viewMode === "history") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="title-text svelte-rtvhgo">대화기록</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (viewMode === "settings") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="title-text svelte-rtvhgo">채팅 설정</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> <div class="header-actions svelte-rtvhgo">`);
    if (viewMode === "chat") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<button${attr_class("icon-btn trigger-toggle svelte-rtvhgo", void 0, { "active": isTriggerMonitoring })}${attr("title", isTriggerMonitoring ? "트리거 모니터링 중지" : "트리거 모니터링 시작")}>`);
      Icon($$renderer2, {
        icon: "solar:driving-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer2.push(`<!----></button>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (isWidgetMode) {
      $$renderer2.push("<!--[-->");
      if (viewMode === "chat") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button class="icon-btn svelte-rtvhgo" title="설정">`);
        Icon($$renderer2, {
          icon: "solar:settings-bold-duotone",
          width: "20",
          height: "20"
        });
        $$renderer2.push(`<!----></button> <button class="icon-btn svelte-rtvhgo" title="대화 기록">`);
        Icon($$renderer2, {
          icon: "solar:history-bold-duotone",
          width: "20",
          height: "20"
        });
        $$renderer2.push(`<!----></button>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (viewMode === "history") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="icon-btn svelte-rtvhgo" title="새 대화">`);
          Icon($$renderer2, {
            icon: "solar:add-circle-bold-duotone",
            width: "20",
            height: "20"
          });
          $$renderer2.push(`<!----></button> <button class="icon-btn svelte-rtvhgo" title="채팅으로 돌아가기">`);
          Icon($$renderer2, {
            icon: "solar:chat-round-bold-duotone",
            width: "20",
            height: "20"
          });
          $$renderer2.push(`<!----></button>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (viewMode === "settings") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="icon-btn svelte-rtvhgo" title="채팅으로 돌아가기">`);
            Icon($$renderer2, {
              icon: "solar:chat-round-bold-duotone",
              width: "20",
              height: "20"
            });
            $$renderer2.push(`<!----></button>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--> <button class="icon-btn svelte-rtvhgo" title="전체 화면으로">`);
      Icon($$renderer2, {
        icon: "solar:maximize-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer2.push(`<!----></button> <button class="icon-btn close svelte-rtvhgo" title="앱 닫기">`);
      Icon($$renderer2, { icon: "solar:close-circle-bold", width: "20", height: "20" });
      $$renderer2.push(`<!----></button>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<button class="icon-btn svelte-rtvhgo"${attr("title", isExpanded ? "크기 축소" : "크기 확대")}>`);
      Icon($$renderer2, {
        icon: isExpanded ? "solar:minimize-square-bold-duotone" : "solar:maximize-square-bold-duotone",
        width: "20",
        height: "20"
      });
      $$renderer2.push(`<!----></button> `);
      if (viewMode === "chat") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button class="icon-btn svelte-rtvhgo" title="설정">`);
        Icon($$renderer2, {
          icon: "solar:settings-bold-duotone",
          width: "20",
          height: "20"
        });
        $$renderer2.push(`<!----></button> <button class="icon-btn svelte-rtvhgo" title="대화 기록">`);
        Icon($$renderer2, {
          icon: "solar:history-bold-duotone",
          width: "20",
          height: "20"
        });
        $$renderer2.push(`<!----></button>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (viewMode === "history") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="icon-btn svelte-rtvhgo" title="새 대화">`);
          Icon($$renderer2, {
            icon: "solar:add-circle-bold-duotone",
            width: "20",
            height: "20"
          });
          $$renderer2.push(`<!----></button> <button class="icon-btn svelte-rtvhgo" title="채팅으로 돌아가기">`);
          Icon($$renderer2, {
            icon: "solar:chat-round-bold-duotone",
            width: "20",
            height: "20"
          });
          $$renderer2.push(`<!----></button>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (viewMode === "settings") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="icon-btn svelte-rtvhgo" title="채팅으로 돌아가기">`);
            Icon($$renderer2, {
              icon: "solar:chat-round-bold-duotone",
              width: "20",
              height: "20"
            });
            $$renderer2.push(`<!----></button>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--> <button class="icon-btn svelte-rtvhgo" title="닫기">`);
      Icon($$renderer2, { icon: "solar:close-circle-bold", width: "20", height: "20" });
      $$renderer2.push(`<!----></button>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="widget-content svelte-rtvhgo"><div${attr_class("view-container svelte-rtvhgo", void 0, { "hidden": viewMode !== "chat" })}>`);
    ChatView($$renderer2);
    $$renderer2.push(`<!----></div> <div${attr_class("view-container svelte-rtvhgo", void 0, { "hidden": viewMode !== "history" })}>`);
    ChatHistoryView($$renderer2);
    $$renderer2.push(`<!----></div> <div${attr_class("view-container svelte-rtvhgo", void 0, { "hidden": viewMode !== "settings" })}>`);
    ChatSettingsView($$renderer2);
    $$renderer2.push(`<!----></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ToastContainer($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const icons = {
      success: "solar:check-circle-bold",
      error: "solar:close-circle-bold",
      warning: "solar:danger-triangle-bold",
      info: "solar:info-circle-bold"
    };
    $$renderer2.push(`<div class="toast-container svelte-cqwvc2"><!--[-->`);
    const each_array = ensure_array_like(toastStore.toasts);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let toast = each_array[$$index];
      $$renderer2.push(`<div${attr_class(`toast toast-${stringify(toast.type)}`, "svelte-cqwvc2")} role="alert">`);
      Icon($$renderer2, { icon: icons[toast.type], width: "20", height: "20" });
      $$renderer2.push(`<!----> <span class="toast-message svelte-cqwvc2">${escape_html(toast.message)}</span> <button class="toast-close svelte-cqwvc2">`);
      Icon($$renderer2, { icon: "solar:close-circle-linear", width: "16", height: "16" });
      $$renderer2.push(`<!----></button></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { children } = $$props;
    getCurrentWindow();
    const sidebarWidth = store_get($$store_subs ??= {}, "$uiStore", uiStore).isSidebarCollapsed ? "5.5rem" : "14rem";
    const isChatOpen = store_get($$store_subs ??= {}, "$uiStore", uiStore).isChatOpen;
    const isWidgetMode = store_get($$store_subs ??= {}, "$uiStore", uiStore).isWidgetMode;
    const isChatExpanded = store_get($$store_subs ??= {}, "$uiStore", uiStore).isChatExpanded;
    $$renderer2.push(`<div${attr_class("layout svelte-12qhfyh", void 0, { "widget-mode": isWidgetMode })}>`);
    if (!isWidgetMode) {
      $$renderer2.push("<!--[-->");
      TitleBar($$renderer2);
      $$renderer2.push(`<!----> `);
      Sidebar($$renderer2);
      $$renderer2.push(`<!----> <main${attr_class("main-content svelte-12qhfyh", void 0, { "chat-open": isChatOpen, "chat-expanded": isChatExpanded })}${attr_style(`margin-left: ${stringify(sidebarWidth)};`)}>`);
      children?.($$renderer2);
      $$renderer2.push(`<!----></main>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (isChatOpen) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div${attr_class("chat-overlay svelte-12qhfyh", void 0, { "fullscreen": isWidgetMode })}>`);
      AIChatWidget($$renderer2);
      $$renderer2.push(`<!----></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    Dialog($$renderer2, {});
    $$renderer2.push(`<!----> `);
    ToastContainer($$renderer2);
    $$renderer2.push(`<!---->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _layout as default
};
