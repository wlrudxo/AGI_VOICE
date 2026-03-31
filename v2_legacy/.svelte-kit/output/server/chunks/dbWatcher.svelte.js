import "clsx";
import { w as writable } from "./index.js";
import { invoke } from "@tauri-apps/api/core";
const POLL_INTERVAL = 2e3;
function createDbWatcher() {
  const { subscribe, set, update } = writable({ lastTimestamp: null, isWatching: false });
  let pollInterval = null;
  let changeCallbacks = [];
  async function checkDbChange() {
    try {
      const data = await invoke("get_db_timestamp");
      const newTimestamp = data.unixTimestamp;
      update((state) => {
        if (state.lastTimestamp === null) {
          return { ...state, lastTimestamp: newTimestamp };
        }
        if (newTimestamp !== state.lastTimestamp) {
          console.log("📊 Database changed detected, triggering refresh...");
          changeCallbacks.forEach((cb) => cb());
          return { ...state, lastTimestamp: newTimestamp };
        }
        return state;
      });
    } catch (err) {
      console.error("Failed to check DB timestamp:", err);
    }
  }
  return {
    subscribe,
    /**
     * DB 변경 감지 시작
     */
    startWatching() {
      update((state) => {
        if (state.isWatching) return state;
        console.log("👀 Starting DB watcher...");
        checkDbChange();
        pollInterval = window.setInterval(checkDbChange, POLL_INTERVAL);
        return { ...state, isWatching: true };
      });
    },
    /**
     * DB 변경 감지 중지
     */
    stopWatching() {
      if (pollInterval !== null) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
      set({ lastTimestamp: null, isWatching: false });
      console.log("🛑 Stopped DB watcher");
    },
    /**
     * DB 변경 시 실행할 콜백 등록
     * @param callback 변경 감지 시 실행될 함수
     * @returns 등록 해제 함수
     */
    onChange(callback) {
      changeCallbacks.push(callback);
      return () => {
        changeCallbacks = changeCallbacks.filter((cb) => cb !== callback);
      };
    },
    /**
     * 즉시 DB 변경 알림 (액션 실행 후 호출)
     * @param delay 딜레이 (ms), 기본값 100ms
     */
    triggerRefresh(delay = 100) {
      setTimeout(
        () => {
          console.log("🔄 DB change triggered manually, refreshing...");
          changeCallbacks.forEach((cb) => cb());
        },
        delay
      );
    }
  };
}
createDbWatcher();
