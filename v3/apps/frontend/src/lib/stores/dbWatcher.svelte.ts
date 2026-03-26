/**
 * 데이터베이스 변경 감지 스토어
 *
 * V2 parity:
 * 1. 액션 실행 후 즉시 알림 (triggerRefresh)
 * 2. 백엔드 DB 타임스탬프 폴링 (fallback)
 */

import { writable } from 'svelte/store';
import { requestJson } from '$lib/backend';

const POLL_INTERVAL = 2000;

interface DbTimestamp {
  unixTimestamp: number | null;
}

interface DbState {
  lastTimestamp: number | null;
  isWatching: boolean;
}

function createDbWatcher() {
  const { subscribe, set, update } = writable<DbState>({
    lastTimestamp: null,
    isWatching: false,
  });

  let pollInterval: number | null = null;
  let changeCallbacks: Array<() => void> = [];

  async function checkDbChange() {
    try {
      const data = await requestJson<DbTimestamp>('/api/settings/db/timestamp');
      const newTimestamp = data.unixTimestamp;

      update((state) => {
        if (state.lastTimestamp === null) {
          return { ...state, lastTimestamp: newTimestamp };
        }

        if (newTimestamp !== state.lastTimestamp) {
          console.log('📊 Database change detected, triggering refresh...');
          changeCallbacks.forEach((callback) => callback());
          return { ...state, lastTimestamp: newTimestamp };
        }

        return state;
      });
    } catch (error) {
      console.error('Failed to check DB timestamp:', error);
    }
  }

  return {
    subscribe,
    startWatching() {
      update((state) => {
        if (state.isWatching) {
          return state;
        }

        console.log('👀 Starting DB watcher...');
        void checkDbChange();
        pollInterval = window.setInterval(checkDbChange, POLL_INTERVAL);

        return { ...state, isWatching: true };
      });
    },
    stopWatching() {
      if (pollInterval !== null) {
        clearInterval(pollInterval);
        pollInterval = null;
      }

      set({ lastTimestamp: null, isWatching: false });
      console.log('🛑 Stopped DB watcher');
    },
    onChange(callback: () => void) {
      changeCallbacks.push(callback);

      return () => {
        changeCallbacks = changeCallbacks.filter((current) => current !== callback);
      };
    },
    triggerRefresh(delay = 100) {
      setTimeout(() => {
        console.log('🔄 DB change triggered manually, refreshing...');
        changeCallbacks.forEach((callback) => callback());
      }, delay);
    },
  };
}

export const dbWatcher = createDbWatcher();
