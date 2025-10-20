/**
 * READ 액션 결과 포맷터
 * 자율주행 연구용으로 재구현 예정
 */

import type { ActionResult } from './executor';

/**
 * READ 액션 결과를 시스템 컨텍스트로 포맷팅
 */
export function formatReadResults(results: ActionResult[]): string {
	const lines: string[] = [];

	for (const result of results) {
		if (result.success && result.result) {
			lines.push(result.result);
		} else if (!result.success && result.error) {
			lines.push(`Error: ${result.error}`);
		}
	}

	return lines.join('\n\n');
}
