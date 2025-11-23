/**
 * AI 액션 실행기 - 파싱된 액션을 Tauri Commands로 변환
 * 자율주행 맵 관리용
 */

import { invoke } from '@tauri-apps/api/core';
import type { Action } from './parser';

export interface ActionResult {
	success: boolean;
	action: Action;
	result?: any;
	error?: string;
}

/**
 * 액션 리스트 실행
 */
export async function executeActions(actions: Action[]): Promise<ActionResult[]> {
	const results: ActionResult[] = [];

	for (const action of actions) {
		try {
			const result = await executeSingleAction(action);
			results.push({
				success: true,
				action,
				result
			});
		} catch (error: any) {
			results.push({
				success: false,
				action,
				error: error.message || String(error)
			});
		}
	}

	return results;
}

/**
 * 단일 액션 실행
 */
async function executeSingleAction(action: Action): Promise<any> {
	const { operation, type, data } = action;

	if (operation === 'create') {
		return await executeCreate(type, data);
	} else if (operation === 'read') {
		return await executeRead(type, data);
	} else if (operation === 'update') {
		return await executeUpdate(type, data);
	} else if (operation === 'delete') {
		return await executeDelete(type, data);
	} else {
		throw new Error(`Unknown operation: ${operation}`);
	}
}

// ==================== CREATE ====================

async function executeCreate(type: string, data: Record<string, any>): Promise<any> {
	if (type === 'map') {
		return await invoke('create_map', { request: data });
	} else {
		throw new Error(`Unknown type for create: ${type}`);
	}
}

// ==================== READ ====================

async function executeRead(type: string, data: Record<string, any>): Promise<string> {
	if (type === 'map') {
		return await readMap(data);
	} else if (type === 'dashboard') {
		return await readDashboard(data);
	} else {
		throw new Error(`Unknown type for read: ${type}`);
	}
}

async function readMap(data: Record<string, any>): Promise<string> {
	if (data.id) {
		// ID로 조회
		try {
			const map: any = await invoke('get_map_by_id', { id: data.id });
			return `[맵 #${map.id}] ${map.name}
설명: ${map.description || '없음'}
카테고리: ${map.category || 'N/A'}, 난이도: ${map.difficulty || 'N/A'}
태그: ${map.tags || '없음'}`;
		} catch (error) {
			return `맵 ID ${data.id}를 찾을 수 없습니다.`;
		}
	} else if (data.category) {
		// 카테고리로 조회
		try {
			const maps: any[] = await invoke('get_maps', {
				category: data.category,
				hasEmbedding: null,
				searchQuery: null
			});
			if (maps.length === 0) {
				return `${data.category} 카테고리에 맵이 없습니다.`;
			}
			const lines = [`📁 ${data.category} 카테고리 맵 (${maps.length}개):`];
			for (const m of maps) {
				lines.push(`  - [#${m.id}] ${m.name}${m.difficulty ? ` (${m.difficulty})` : ''}`);
			}
			return lines.join('\n');
		} catch (error) {
			return `카테고리 조회 실패: ${error}`;
		}
	} else if (data.name) {
		// 이름으로 검색
		try {
			const maps: any[] = await invoke('get_maps', {
				category: null,
				hasEmbedding: null,
				searchQuery: data.name
			});
			if (maps.length === 0) {
				return `"${data.name}"로 검색된 맵이 없습니다.`;
			}
			const lines = [`🔍 "${data.name}" 검색 결과 (${maps.length}개):`];
			for (const m of maps) {
				lines.push(`  - [#${m.id}] ${m.name}${m.category ? ` [${m.category}]` : ''}`);
			}
			return lines.join('\n');
		} catch (error) {
			return `검색 실패: ${error}`;
		}
	} else {
		// 전체 조회
		try {
			const maps: any[] = await invoke('get_maps', {
				category: null,
				hasEmbedding: null,
				searchQuery: null
			});
			return `📋 전체 맵: ${maps.length}개`;
		} catch (error) {
			return `맵 조회 실패: ${error}`;
		}
	}
}

async function readDashboard(data: Record<string, any>): Promise<string> {
	try {
		const count: number = await invoke('get_map_count');
		return `📊 대시보드 현황:
총 맵 개수: ${count}개`;
	} catch (error) {
		return `대시보드 조회 실패: ${error}`;
	}
}

// ==================== UPDATE ====================

async function executeUpdate(type: string, data: Record<string, any>): Promise<any> {
	if (type === 'map') {
		const { id, ...updateData } = data;
		return await invoke('update_map', { id, request: updateData });
	} else {
		throw new Error(`Unknown type for update: ${type}`);
	}
}

// ==================== DELETE ====================

async function executeDelete(type: string, data: Record<string, any>): Promise<any> {
	if (type === 'map') {
		return await invoke('delete_map', { id: data.id });
	} else {
		throw new Error(`Unknown type for delete: ${type}`);
	}
}
