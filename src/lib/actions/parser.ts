/**
 * AI 응답 파싱 - 통합 CRUD 태그 시스템
 * Python parser.py의 TypeScript 포팅
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

// 식사 타입 매핑 (한글 → 영어)
const MEAL_TYPE_MAP: Record<string, string> = {
	'아침': 'breakfast',
	'점심': 'lunch',
	'저녁': 'dinner',
	'간식': 'snack',
	'보충제': 'supplement',
	'breakfast': 'breakfast',
	'lunch': 'lunch',
	'dinner': 'dinner',
	'snack': 'snack',
	'supplement': 'supplement'
};

// Mission status 매핑
const MISSION_STATUS_MAP: Record<string, string> = {
	'대기': 'pending',
	'진행중': 'in_progress',
	'완료': 'completed',
	'실패': 'failed',
	'pending': 'pending',
	'in_progress': 'in_progress',
	'completed': 'completed',
	'failed': 'failed'
};

/**
 * 응답에서 액션 태그 파싱
 */
export function parseActions(response: string): Action[] {
	const actions: Action[] = [];
	const tagPattern = /<([^|>]+)(?:\|([^>]+))?>/g;
	let match;

	while ((match = tagPattern.exec(response)) !== null) {
		const actionType = match[1].trim();
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
 */
export function parseWithSegments(response: string): ParsedSegment[] {
	const segments: ParsedSegment[] = [];
	const tagPattern = /<([^|>]+)(?:\|([^>]+))?>/g;
	let lastEnd = 0;
	let match;

	while ((match = tagPattern.exec(response)) !== null) {
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
		const actionType = match[1].trim();
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
	if (actionType === 'meal') {
		return createMeal(fields);
	} else if (actionType === 'exercise') {
		return createExercise(fields);
	} else if (actionType === 'weight') {
		return createWeight(fields);
	} else if (actionType === 'mission') {
		return createMission(fields);
	}

	// ==================== UPDATE ====================
	else if (actionType === 'update_meal') {
		return updateMeal(fields);
	} else if (actionType === 'update_exercise') {
		return updateExercise(fields);
	} else if (actionType === 'update_weight') {
		return updateWeight(fields);
	} else if (actionType === 'update_mission') {
		return updateMission(fields);
	}

	// ==================== DELETE ====================
	else if (actionType === 'delete_meal') {
		return deleteMeal(fields);
	} else if (actionType === 'delete_exercise') {
		return deleteExercise(fields);
	} else if (actionType === 'delete_weight') {
		return deleteWeight(fields);
	} else if (actionType === 'delete_mission') {
		return deleteMission(fields);
	}

	// ==================== READ ====================
	else if (actionType === 'read_meal') {
		return readMeal(fields);
	} else if (actionType === 'read_exercise') {
		return readExercise(fields);
	} else if (actionType === 'read_weight') {
		return readWeight(fields);
	} else if (actionType === 'read_mission') {
		return readMission(fields);
	} else if (actionType === 'read_dashboard') {
		return readDashboard(fields);
	}

	return null;
}

// ==================== CREATE 메서드 ====================

function createMeal(fields: Record<string, string>): Action {
	const mealType = fields.meal_type || 'snack';
	const mealTypeEn = MEAL_TYPE_MAP[mealType] || 'snack';

	return {
		operation: 'create',
		type: 'meal',
		data: {
			foodName: fields.name || '',
			calories: fields.calories ? parseInt(fields.calories) : null,
			protein: fields.protein ? parseFloat(fields.protein) : null,
			carbs: fields.carbs ? parseFloat(fields.carbs) : null,
			fat: fields.fat ? parseFloat(fields.fat) : null,
			mealType: mealTypeEn,
			mealDate: fields.date || new Date().toISOString().split('T')[0]
		}
	};
}

function createExercise(fields: Record<string, string>): Action {
	return {
		operation: 'create',
		type: 'exercise',
		data: {
			exerciseName: fields.name || '',
			duration: parseInt(fields.duration || '0'),
			calories: fields.calories ? parseInt(fields.calories) : null,
			category: fields.category || null,
			exerciseDate: fields.date || new Date().toISOString().split('T')[0]
		}
	};
}

function createWeight(fields: Record<string, string>): Action {
	return {
		operation: 'create',
		type: 'weight',
		data: {
			weight: parseFloat(fields.weight || '0'),
			note: fields.note || null,
			measuredDate: fields.date || new Date().toISOString().split('T')[0]
		}
	};
}

function createMission(fields: Record<string, string>): Action {
	const data: Record<string, any> = {
		missionTitle: fields.name || '',
		description: fields.description || null,
		aiComment: fields.ai_comment || null,
		deadline: fields.deadline || null
	};

	// status 필드가 있으면 추가 (한글 -> 영어 변환)
	if (fields.status) {
		data.status = MISSION_STATUS_MAP[fields.status] || fields.status;
	}

	return {
		operation: 'create',
		type: 'mission',
		data
	};
}

// ==================== UPDATE 메서드 ====================

function updateMeal(fields: Record<string, string>): Action {
	const data: Record<string, any> = { id: parseInt(fields.id) };

	if (fields.name) data.foodName = fields.name;
	if (fields.calories) data.calories = parseInt(fields.calories);
	if (fields.protein) data.protein = parseFloat(fields.protein);
	if (fields.carbs) data.carbs = parseFloat(fields.carbs);
	if (fields.fat) data.fat = parseFloat(fields.fat);
	if (fields.meal_type) {
		data.mealType = MEAL_TYPE_MAP[fields.meal_type] || fields.meal_type;
	}
	if (fields.date) data.mealDate = fields.date;

	return {
		operation: 'update',
		type: 'meal',
		data
	};
}

function updateExercise(fields: Record<string, string>): Action {
	const data: Record<string, any> = { id: parseInt(fields.id) };

	if (fields.name) data.exerciseName = fields.name;
	if (fields.duration) data.duration = parseInt(fields.duration);
	if (fields.calories) data.calories = parseInt(fields.calories);
	if (fields.category) data.category = fields.category;
	if (fields.date) data.exerciseDate = fields.date;

	return {
		operation: 'update',
		type: 'exercise',
		data
	};
}

function updateWeight(fields: Record<string, string>): Action {
	const data: Record<string, any> = { id: parseInt(fields.id) };

	if (fields.weight) data.weight = parseFloat(fields.weight);
	if (fields.note) data.note = fields.note;
	if (fields.date) data.measuredDate = fields.date;

	return {
		operation: 'update',
		type: 'weight',
		data
	};
}

function updateMission(fields: Record<string, string>): Action {
	const data: Record<string, any> = { id: parseInt(fields.id) };

	if (fields.name) data.missionTitle = fields.name;
	if (fields.description) data.description = fields.description;
	if (fields.status) {
		data.status = MISSION_STATUS_MAP[fields.status] || fields.status;
	}
	if (fields.ai_comment) data.aiComment = fields.ai_comment;
	if (fields.completion_comment) data.completionComment = fields.completion_comment;
	if (fields.deadline) data.deadline = fields.deadline;

	return {
		operation: 'update',
		type: 'mission',
		data
	};
}

// ==================== DELETE 메서드 ====================

function deleteMeal(fields: Record<string, string>): Action {
	return {
		operation: 'delete',
		type: 'meal',
		data: {
			id: fields.id ? parseInt(fields.id) : null,
			date: fields.date || null
		}
	};
}

function deleteExercise(fields: Record<string, string>): Action {
	return {
		operation: 'delete',
		type: 'exercise',
		data: {
			id: fields.id ? parseInt(fields.id) : null,
			date: fields.date || null
		}
	};
}

function deleteWeight(fields: Record<string, string>): Action {
	return {
		operation: 'delete',
		type: 'weight',
		data: {
			id: fields.id ? parseInt(fields.id) : null,
			date: fields.date || null
		}
	};
}

function deleteMission(fields: Record<string, string>): Action {
	return {
		operation: 'delete',
		type: 'mission',
		data: {
			id: parseInt(fields.id)
		}
	};
}

// ==================== READ 메서드 ====================

function readMeal(fields: Record<string, string>): Action {
	return {
		operation: 'read',
		type: 'meal',
		data: {
			id: fields.id ? parseInt(fields.id) : null,
			date: fields.date || null
		}
	};
}

function readExercise(fields: Record<string, string>): Action {
	return {
		operation: 'read',
		type: 'exercise',
		data: {
			id: fields.id ? parseInt(fields.id) : null,
			date: fields.date || null
		}
	};
}

function readWeight(fields: Record<string, string>): Action {
	return {
		operation: 'read',
		type: 'weight',
		data: {
			id: fields.id ? parseInt(fields.id) : null,
			date: fields.date || null
		}
	};
}

function readMission(fields: Record<string, string>): Action {
	const data: Record<string, any> = {};

	if (fields.id) data.id = parseInt(fields.id);
	if (fields.status) {
		data.status = MISSION_STATUS_MAP[fields.status] || fields.status;
	}

	return {
		operation: 'read',
		type: 'mission',
		data
	};
}

function readDashboard(fields: Record<string, string>): Action {
	return {
		operation: 'read',
		type: 'dashboard',
		data: {
			date: fields.date || null,
			days: fields.days ? parseInt(fields.days) : null
		}
	};
}

// ==================== Helper Functions ====================

/**
 * 액션 타입에 따른 한글 레이블 반환
 */
export function getActionLabel(actionType: string): string {
	const labels: Record<string, string> = {
		meal: '식단 추가',
		exercise: '운동 추가',
		weight: '체중 추가',
		mission: '미션 생성',
		update_meal: '식단 수정',
		update_exercise: '운동 수정',
		update_weight: '체중 수정',
		update_mission: '미션 수정',
		delete_meal: '식단 삭제',
		delete_exercise: '운동 삭제',
		delete_weight: '체중 삭제',
		delete_mission: '미션 삭제',
		read_meal: '식단 조회',
		read_exercise: '운동 조회',
		read_weight: '체중 조회',
		read_mission: '미션 조회',
		read_dashboard: '대시보드 조회'
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
