/**
 * AI 액션 실행기 - 파싱된 액션을 Tauri Commands로 변환
 * Migrated from Python executor.py + FastAPI to Tauri
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
	if (type === 'meal') {
		return await invoke('create_meal', { meal: data });
	} else if (type === 'exercise') {
		return await invoke('create_exercise', { exercise: data });
	} else if (type === 'weight') {
		return await invoke('create_weight', { weightData: data });
	} else if (type === 'mission') {
		return await invoke('create_mission', { mission: data });
	} else {
		throw new Error(`Unknown type for create: ${type}`);
	}
}

// ==================== READ ====================

async function executeRead(type: string, data: Record<string, any>): Promise<string> {
	if (type === 'meal') {
		return await readMeal(data);
	} else if (type === 'exercise') {
		return await readExercise(data);
	} else if (type === 'weight') {
		return await readWeight(data);
	} else if (type === 'mission') {
		return await readMission(data);
	} else if (type === 'dashboard') {
		return await readDashboard(data);
	} else {
		throw new Error(`Unknown type for read: ${type}`);
	}
}

async function readMeal(data: Record<string, any>): Promise<string> {
	if (data.id) {
		// ID로 조회
		try {
			const meal: any = await invoke('get_meal_by_id', { id: data.id });
			return `[식단 #${meal.id}] ${meal.mealDate} ${meal.mealType}: ${meal.foodName} (${meal.calories}kcal)`;
		} catch (error) {
			return `ID ${data.id}인 식단을 찾을 수 없습니다.`;
		}
	} else if (data.date) {
		// 날짜로 조회
		try {
			const meals: any[] = await invoke('get_meals', { mealDate: data.date });

			if (meals.length === 0) {
				return `${data.date}에 기록된 식단이 없습니다.`;
			}

			const totalCalories = meals.reduce((sum: number, m: any) => sum + (m.calories || 0), 0);
			const lines = [`📅 ${data.date} 식단 (총 ${meals.length}개, ${totalCalories}kcal):`];
			for (const meal of meals) {
				lines.push(`  - [${meal.mealType}] ${meal.foodName} (${meal.calories}kcal) [ID: ${meal.id}]`);
			}
			return lines.join('\n');
		} catch (error) {
			return `${data.date}에 기록된 식단을 조회할 수 없습니다.`;
		}
	} else {
		return '식단 조회를 위해 ID 또는 날짜를 지정해주세요.';
	}
}

async function readExercise(data: Record<string, any>): Promise<string> {
	if (data.id) {
		// ID로 조회
		try {
			const exercise: any = await invoke('get_exercise_by_id', { id: data.id });
			return `[운동 #${exercise.id}] ${exercise.exerciseDate}: ${exercise.exerciseName} (${exercise.duration}분, ${exercise.category})`;
		} catch (error) {
			return `ID ${data.id}인 운동을 찾을 수 없습니다.`;
		}
	} else if (data.date) {
		// 날짜로 조회
		try {
			const exercises: any[] = await invoke('get_exercises', { exerciseDate: data.date });

			if (exercises.length === 0) {
				return `${data.date}에 기록된 운동이 없습니다.`;
			}

			const totalDuration = exercises.reduce((sum: number, e: any) => sum + e.duration, 0);
			const lines = [`📅 ${data.date} 운동 (총 ${exercises.length}개, ${totalDuration}분):`];
			for (const exercise of exercises) {
				lines.push(`  - ${exercise.exerciseName} (${exercise.duration}분, ${exercise.category}) [ID: ${exercise.id}]`);
			}
			return lines.join('\n');
		} catch (error) {
			return `${data.date}에 기록된 운동을 조회할 수 없습니다.`;
		}
	} else {
		return '운동 조회를 위해 ID 또는 날짜를 지정해주세요.';
	}
}

async function readWeight(data: Record<string, any>): Promise<string> {
	if (data.id) {
		// ID로 조회
		try {
			const weight: any = await invoke('get_weight_by_id', { id: data.id });
			return `[체중 #${weight.id}] ${weight.measuredDate}: ${weight.weight}kg (${weight.note || ''})`;
		} catch (error) {
			return `ID ${data.id}인 체중 기록을 찾을 수 없습니다.`;
		}
	} else if (data.date) {
		// 날짜로 조회
		try {
			const weight: any = await invoke('get_weight_by_date', { date: data.date });
			return `📅 ${data.date} 체중: ${weight.weight}kg (${weight.note || ''}) [ID: ${weight.id}]`;
		} catch (error) {
			return `${data.date}에 기록된 체중이 없습니다.`;
		}
	} else {
		return '체중 조회를 위해 ID 또는 날짜를 지정해주세요.';
	}
}

async function readMission(data: Record<string, any>): Promise<string> {
	if (data.id) {
		// ID로 조회
		try {
			const mission: any = await invoke('get_mission_by_id', { id: data.id });
			return `[미션 #${mission.id}] ${mission.missionTitle} (${mission.status}) - ${mission.description || ''}`;
		} catch (error) {
			return `ID ${data.id}인 미션을 찾을 수 없습니다.`;
		}
	} else if (data.status) {
		// 상태로 조회
		const status = data.status;

		try {
			const missions: any[] = status.toLowerCase() === 'all'
				? await invoke('get_missions', { status: undefined })
				: await invoke('get_missions', { status });

			if (missions.length === 0) {
				return status.toLowerCase() === 'all'
					? '등록된 미션이 없습니다.'
					: `상태가 '${status}'인 미션이 없습니다.`;
			}

			const title = status.toLowerCase() === 'all' ? '전체 미션' : `${status} 미션`;
			const lines = [`📋 ${title} (${missions.length}개):`];
			for (const mission of missions) {
				const deadlineStr = mission.deadline ? `, 마감: ${mission.deadline}` : '';
				lines.push(`  - [${mission.id}] ${mission.missionTitle} (${mission.status})${deadlineStr}`);
			}
			return lines.join('\n');
		} catch (error) {
			return '미션을 조회할 수 없습니다.';
		}
	} else {
		// 전체 조회 (최근 10개)
		try {
			const missions: any[] = await invoke('get_missions', { status: undefined });

			if (missions.length === 0) {
				return '등록된 미션이 없습니다.';
			}

			const lines = [`📋 최근 미션 (${missions.length}개):`];
			for (const mission of missions.slice(0, 10)) {
				lines.push(`  - [${mission.id}] ${mission.missionTitle} (${mission.status})`);
			}
			return lines.join('\n');
		} catch (error) {
			return '미션을 조회할 수 없습니다.';
		}
	}
}

async function readDashboard(data: Record<string, any>): Promise<string> {
	if (data.days) {
		// 주간 대시보드
		try {
			const dashboard: any = await invoke('get_weekly_dashboard', { days: parseInt(data.days) });
			const lines = [`📊 주간 대시보드 (${data.days}일)`];

			if (dashboard.dailyData) {
				for (const day of dashboard.dailyData) {
					const weightStr = day.weight ? `${day.weight}kg` : '-';
					const mealCalories = day.meals?.totalCalories || 0;
					const exerciseDuration = day.exercises?.totalDuration || 0;

					lines.push(`\n${day.date}: 체중 ${weightStr}, 식단 ${mealCalories}kcal, 운동 ${exerciseDuration}분`);

					if (day.meals?.items && day.meals.items.length > 0) {
						// meal byType이 있으면 타입별로 표시
						if (day.meals.byType) {
							for (const [mealType, items] of Object.entries(day.meals.byType)) {
								for (const item of items as string[]) {
									lines.push(`  🍽️ [${mealType}] ${item}`);
								}
							}
						} else {
							for (const item of day.meals.items) {
								lines.push(`  🍽️ ${item}`);
							}
						}
					}

					if (day.exercises?.items && day.exercises.items.length > 0) {
						for (const item of day.exercises.items) {
							lines.push(`  💪 ${item}`);
						}
					}
				}
			}

			return lines.join('\n');
		} catch (error) {
			return '주간 대시보드를 조회할 수 없습니다.';
		}
	} else {
		// 일일 대시보드
		try {
			const dashboard: any = await invoke('get_dashboard', { targetDate: data.date || undefined });
			const targetDate = dashboard.date || data.date || new Date().toISOString().split('T')[0];
			const lines = [`📊 ${targetDate} 대시보드`];

			if (dashboard.weight) {
				lines.push(`\n⚖️ 체중: ${dashboard.weight.weight}kg`);
			}

			if (dashboard.meals && dashboard.meals.meals && dashboard.meals.meals.length > 0) {
				const totalCalories = dashboard.meals.totalCalories;
				lines.push(`\n🍽️ 식단: ${dashboard.meals.mealCount}개, 총 ${totalCalories}kcal`);
				for (const meal of dashboard.meals.meals) {
					lines.push(`  - [${meal.mealType}] ${meal.foodName} (${meal.calories}kcal)`);
				}
			}

			if (dashboard.exercises && dashboard.exercises.exercises && dashboard.exercises.exercises.length > 0) {
				const totalDuration = dashboard.exercises.totalDuration;
				lines.push(`\n💪 운동: ${dashboard.exercises.exerciseCount}개, 총 ${totalDuration}분`);
				for (const exercise of dashboard.exercises.exercises) {
					lines.push(`  - ${exercise.exerciseName} (${exercise.duration}분)`);
				}
			}

			if (dashboard.currentMissions && dashboard.currentMissions.length > 0) {
				lines.push(`\n📋 진행중인 미션: ${dashboard.currentMissions.length}개`);
				for (const mission of dashboard.currentMissions) {
					lines.push(`  - ${mission.missionTitle}`);
				}
			}

			return lines.join('\n');
		} catch (error) {
			return '일일 대시보드를 조회할 수 없습니다.';
		}
	}
}

// ==================== UPDATE ====================

async function executeUpdate(type: string, data: Record<string, any>): Promise<any> {
	const id = data.id;
	delete data.id;

	if (type === 'meal') {
		return await invoke('update_meal', { id, meal: data });
	} else if (type === 'exercise') {
		return await invoke('update_exercise', { id, exercise: data });
	} else if (type === 'weight') {
		return await invoke('update_weight', { id, weightData: data });
	} else if (type === 'mission') {
		return await invoke('update_mission', { id, mission: data });
	} else {
		throw new Error(`Unknown type for update: ${type}`);
	}
}

// ==================== DELETE ====================

async function executeDelete(type: string, data: Record<string, any>): Promise<any> {
	if (type === 'meal') {
		if (data.id) {
			await invoke('delete_meal', { id: data.id });
			return { message: `Meal #${data.id} deleted` };
		} else if (data.date) {
			await invoke('delete_meals_by_date', { date: data.date });
			return { message: `Meals deleted for ${data.date}` };
		}
	} else if (type === 'exercise') {
		if (data.id) {
			await invoke('delete_exercise', { id: data.id });
			return { message: `Exercise #${data.id} deleted` };
		} else if (data.date) {
			await invoke('delete_exercises_by_date', { date: data.date });
			return { message: `Exercises deleted for ${data.date}` };
		}
	} else if (type === 'weight') {
		if (data.id) {
			await invoke('delete_weight', { id: data.id });
			return { message: `Weight #${data.id} deleted` };
		} else if (data.date) {
			await invoke('delete_weight_by_date', { date: data.date });
			return { message: `Weight deleted for ${data.date}` };
		}
	} else if (type === 'mission') {
		await invoke('delete_mission', { id: data.id });
		return { message: `Mission #${data.id} deleted` };
	} else {
		throw new Error(`Unknown type for delete: ${type}`);
	}

	throw new Error('ID or date required for deletion');
}
