/**
 * READ 결과 포맷터 - READ 액션 결과를 system 메시지로 포맷팅
 */

import type { ActionResult } from './executor';

/**
 * READ 액션 결과들을 system 메시지로 포맷팅
 *
 * @param results READ 액션 실행 결과 리스트
 * @returns Claude에게 전달할 system 컨텍스트 문자열
 */
export function formatReadResults(results: ActionResult[]): string {
	const contextParts: string[] = [];

	for (const result of results) {
		if (result.success && result.result) {
			// READ 결과는 이미 executor에서 포맷된 문자열로 반환됨
			contextParts.push(result.result);
		} else if (!result.success) {
			// 실패한 READ도 컨텍스트에 포함 (에러 메시지)
			contextParts.push(`⚠️ 조회 실패: ${result.error}`);
		}
	}

	if (contextParts.length === 0) {
		return '';
	}

	// 구분선으로 각 결과를 구분
	return contextParts.join('\n\n---\n\n');
}

/**
 * 액션 실행 결과를 사용자 친화적인 메시지로 변환
 *
 * @param results 모든 액션 실행 결과
 * @returns 사용자에게 표시할 메시지
 */
export function formatActionSummary(results: ActionResult[]): string {
	const successCount = results.filter(r => r.success).length;
	const failureCount = results.filter(r => !r.success).length;

	if (failureCount === 0) {
		if (successCount === 1) {
			return '✅ 작업이 완료되었습니다.';
		} else {
			return `✅ ${successCount}개의 작업이 완료되었습니다.`;
		}
	} else {
		if (successCount === 0) {
			return `❌ ${failureCount}개의 작업이 실패했습니다.`;
		} else {
			return `⚠️ ${successCount}개 성공, ${failureCount}개 실패`;
		}
	}
}

/**
 * 개별 액션 결과를 사용자 친화적인 메시지로 변환
 *
 * @param result 액션 실행 결과
 * @returns 사용자에게 표시할 메시지
 */
export function formatSingleActionResult(result: ActionResult): string {
	const { action, success, error } = result;
	const { operation, type } = action;

	const typeLabel: Record<string, string> = {
		meal: '식단',
		exercise: '운동',
		weight: '체중',
		mission: '미션',
		dashboard: '대시보드'
	};

	const operationLabel: Record<string, string> = {
		create: '추가',
		read: '조회',
		update: '수정',
		delete: '삭제'
	};

	const label = `${typeLabel[type] || type} ${operationLabel[operation] || operation}`;

	if (success) {
		return `✅ ${label} 완료`;
	} else {
		return `❌ ${label} 실패: ${error}`;
	}
}
