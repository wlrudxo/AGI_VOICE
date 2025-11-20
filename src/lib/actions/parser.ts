/**
 * AI 응답 파싱 - 통합 액션 태그 시스템
 * 자율주행 연구용으로 재구현 예정
 */

export interface Action {
	operation: 'create' | 'read' | 'update' | 'delete';
	type: string;
	data: Record<string, any>;
}

export interface ParsedSegment {
	type: 'text' | 'action';
	content?: string;
	action?: Action;
	label?: string;
}

/**
 * 응답에서 액션 태그 파싱
 */
export function parseActions(response: string): Action[] {
	const actions: Action[] = [];
	// TODO: 자율주행 연구용 태그 파싱 로직 구현
	return actions;
}

/**
 * 응답을 태그 위치 기준으로 분할하여 순서대로 반환
 */
export function parseWithSegments(response: string): ParsedSegment[] {
	// 태그가 없으면 전체를 text로 반환
	return [{
		type: 'text',
		content: response
	}];
}

/**
 * 액션 타입에 따른 한글 레이블 반환
 */
export function getActionLabel(actionType: string): string {
	const labels: Record<string, string> = {
		// TODO: 자율주행 연구용 액션 레이블 정의
	};
	return labels[actionType] || actionType;
}

/**
 * 응답에서 태그 제거하여 깨끗한 텍스트만 반환
 */
export function removeActionTags(response: string): string {
	const tagPattern = /<([^|>]+)(?:\|([^>]+))?>/g;
	return response.replace(tagPattern, '').trim();
}
