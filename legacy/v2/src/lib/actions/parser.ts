/**
 * AI 응답 파싱 - 통합 CRUD 태그 시스템
 * 자율주행 맵 관리용
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

// Known action types that should be parsed as tags
const KNOWN_ACTION_TYPES = new Set([
	'map', 'update_map', 'delete_map', 'read_map', 'read_dashboard'
]);

/**
 * 응답에서 액션 태그 파싱
 * - 줄바꿈이 포함된 태그는 무시
 * - 알려진 액션 타입만 처리
 */
export function parseActions(response: string): Action[] {
	const actions: Action[] = [];
	// 줄바꿈이 없는 태그만 매칭 ([^\n|>] 로 줄바꿈 제외)
	const tagPattern = /<([^\n|>]+)(?:\|([^\n>]+))?>/g;
	let match;

	while ((match = tagPattern.exec(response)) !== null) {
		const actionType = match[1].trim();

		// 알려진 액션 타입이 아니면 무시
		if (!KNOWN_ACTION_TYPES.has(actionType)) {
			continue;
		}

		const fieldsStr = match[2]?.trim();

		const fields = parseFields(fieldsStr);
		const action = processAction(actionType, fields);

		if (action) {
			actions.push(action);
		}
	}

	return actions;
}

/**
 * 응답을 태그 위치 기준으로 분할하여 순서대로 반환
 * - 줄바꿈이 포함된 태그는 무시
 * - 알려진 액션 타입만 처리
 */
export function parseWithSegments(response: string): ParsedSegment[] {
	const segments: ParsedSegment[] = [];
	// 줄바꿈이 없는 태그만 매칭
	const tagPattern = /<([^\n|>]+)(?:\|([^\n>]+))?>/g;
	let lastEnd = 0;
	let match;

	while ((match = tagPattern.exec(response)) !== null) {
		const actionType = match[1].trim();

		// 알려진 액션 타입이 아니면 일반 텍스트로 처리 (skip하지 않고 계속)
		if (!KNOWN_ACTION_TYPES.has(actionType)) {
			continue;
		}

		// 태그 이전 텍스트 추가
		if (match.index > lastEnd) {
			const textBefore = response.substring(lastEnd, match.index).trim();
			if (textBefore) {
				segments.push({
					type: 'text',
					content: textBefore
				});
			}
		}

		// 태그 파싱
		const fieldsStr = match[2]?.trim();
		const fields = parseFields(fieldsStr);
		const action = processAction(actionType, fields);

		if (action) {
			segments.push({
				type: 'action',
				action: action,
				label: getActionLabel(actionType)
			});
		}

		lastEnd = match.index + match[0].length;
	}

	// 마지막 태그 이후 텍스트 추가
	if (lastEnd < response.length) {
		const textAfter = response.substring(lastEnd).trim();
		if (textAfter) {
			segments.push({
				type: 'text',
				content: textAfter
			});
		}
	}

	// 태그가 없으면 전체를 text로 반환
	if (segments.length === 0) {
		segments.push({
			type: 'text',
			content: response
		});
	}

	return segments;
}

/**
 * field:value|field:value 형식을 객체로 파싱
 */
function parseFields(fieldsStr?: string): Record<string, string> {
	const fields: Record<string, string> = {};
	if (!fieldsStr) return fields;

	for (const part of fieldsStr.split('|')) {
		if (part.includes(':')) {
			const [key, ...valueParts] = part.split(':');
			fields[key.trim()] = valueParts.join(':').trim();
		}
	}

	return fields;
}

/**
 * 액션 타입별 처리
 */
function processAction(actionType: string, fields: Record<string, string>): Action | null {
	// ==================== CREATE ====================
	if (actionType === 'map') {
		return createMap(fields);
	}

	// ==================== UPDATE ====================
	else if (actionType === 'update_map') {
		return updateMap(fields);
	}

	// ==================== DELETE ====================
	else if (actionType === 'delete_map') {
		return deleteMap(fields);
	}

	// ==================== READ ====================
	else if (actionType === 'read_map') {
		return readMap(fields);
	} else if (actionType === 'read_dashboard') {
		return readDashboard(fields);
	}

	return null;
}

// ==================== CREATE 메서드 ====================

function createMap(fields: Record<string, string>): Action {
	return {
		operation: 'create',
		type: 'map',
		data: {
			name: fields.name || '',
			description: fields.description || null,
			nodeXml: fields.node_xml || fields.nodeXml || null,
			edgeXml: fields.edge_xml || fields.edgeXml || null,
			tags: fields.tags || null,
			category: fields.category || null,
			difficulty: fields.difficulty || null,
			metadata: fields.metadata || null
		}
	};
}

// ==================== UPDATE 메서드 ====================

function updateMap(fields: Record<string, string>): Action {
	const data: Record<string, any> = { id: parseInt(fields.id) };

	if (fields.name) data.name = fields.name;
	if (fields.description) data.description = fields.description;
	if (fields.node_xml || fields.nodeXml) data.nodeXml = fields.node_xml || fields.nodeXml;
	if (fields.edge_xml || fields.edgeXml) data.edgeXml = fields.edge_xml || fields.edgeXml;
	if (fields.tags) data.tags = fields.tags;
	if (fields.category) data.category = fields.category;
	if (fields.difficulty) data.difficulty = fields.difficulty;
	if (fields.metadata) data.metadata = fields.metadata;

	return {
		operation: 'update',
		type: 'map',
		data
	};
}

// ==================== DELETE 메서드 ====================

function deleteMap(fields: Record<string, string>): Action {
	return {
		operation: 'delete',
		type: 'map',
		data: {
			id: parseInt(fields.id)
		}
	};
}

// ==================== READ 메서드 ====================

function readMap(fields: Record<string, string>): Action {
	const data: Record<string, any> = {};

	if (fields.id) data.id = parseInt(fields.id);
	if (fields.category) data.category = fields.category;
	if (fields.name) data.name = fields.name;

	return {
		operation: 'read',
		type: 'map',
		data
	};
}

function readDashboard(fields: Record<string, string>): Action {
	return {
		operation: 'read',
		type: 'dashboard',
		data: {}
	};
}

// ==================== Helper Functions ====================

/**
 * 액션 타입에 따른 한글 레이블 반환
 */
export function getActionLabel(actionType: string): string {
	const labels: Record<string, string> = {
		map: '맵 추가',
		update_map: '맵 수정',
		delete_map: '맵 삭제',
		read_map: '맵 조회',
		read_dashboard: '대시보드 조회'
	};
	return labels[actionType] || actionType;
}

/**
 * 응답에서 알려진 액션 태그만 제거하여 깨끗한 텍스트만 반환
 * - 줄바꿈이 포함된 태그는 제거하지 않음
 * - 알려진 액션 타입만 제거
 */
export function removeActionTags(response: string): string {
	const tagPattern = /<([^\n|>]+)(?:\|([^\n>]+))?>/g;
	return response.replace(tagPattern, (match, actionType) => {
		// 알려진 액션 타입만 제거
		if (KNOWN_ACTION_TYPES.has(actionType.trim())) {
			return '';
		}
		// 알려지지 않은 태그는 그대로 유지
		return match;
	}).trim();
}
