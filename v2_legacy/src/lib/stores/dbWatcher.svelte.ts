/**
 * 데이터베이스 변경 감지 스토어
 *
 * 두 가지 방식으로 DB 변경 감지:
 * 1. 액션 실행 후 즉시 알림 (triggerRefresh)
 * 2. 백엔드 DB 파일의 수정 시간 폴링 (fallback)
 */

import { writable } from 'svelte/store';
import { invoke } from '@tauri-apps/api/core';

const POLL_INTERVAL = 2000; // 2초마다 체크

interface DbState {
	lastTimestamp: number | null;
	isWatching: boolean;
}

function createDbWatcher() {
	const { subscribe, set, update } = writable<DbState>({
		lastTimestamp: null,
		isWatching: false
	});

	let pollInterval: number | null = null;
	let changeCallbacks: Array<() => void> = [];

	async function checkDbChange() {
		try {
			const data = await invoke('get_db_timestamp');
			const newTimestamp = data.unixTimestamp;

			update((state) => {
				// 첫 번째 체크인 경우 타임스탬프만 저장
				if (state.lastTimestamp === null) {
					return { ...state, lastTimestamp: newTimestamp };
				}

				// 타임스탬프가 변경되었으면 콜백 실행
				if (newTimestamp !== state.lastTimestamp) {
					console.log('📊 Database changed detected, triggering refresh...');
					changeCallbacks.forEach((cb) => cb());
					return { ...state, lastTimestamp: newTimestamp };
				}

				return state;
			});
		} catch (err) {
			console.error('Failed to check DB timestamp:', err);
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

				console.log('👀 Starting DB watcher...');

				// 초기 타임스탬프 가져오기
				checkDbChange();

				// 주기적으로 체크
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
			console.log('🛑 Stopped DB watcher');
		},

		/**
		 * DB 변경 시 실행할 콜백 등록
		 * @param callback 변경 감지 시 실행될 함수
		 * @returns 등록 해제 함수
		 */
		onChange(callback: () => void) {
			changeCallbacks.push(callback);

			// 등록 해제 함수 반환
			return () => {
				changeCallbacks = changeCallbacks.filter((cb) => cb !== callback);
			};
		},

		/**
		 * 즉시 DB 변경 알림 (액션 실행 후 호출)
		 * @param delay 딜레이 (ms), 기본값 100ms
		 */
		triggerRefresh(delay: number = 100) {
			setTimeout(() => {
				console.log('🔄 DB change triggered manually, refreshing...');
				changeCallbacks.forEach((cb) => cb());
			}, delay);
		}
	};
}

export const dbWatcher = createDbWatcher();
