/**
 * AI 설정 스토어
 * - 현재 선택된 템플릿, 캐릭터 관리
 * - LocalStorage에 저장
 */

const STORAGE_KEY = 'agi_voice_config';

interface AIConfig {
	selectedTemplateId: number | null;
	selectedCharacterId: number | null;
	userInfo: string;
	finalMessage: string;
}

function createAIConfigStore() {
	let config = $state<AIConfig>({
		selectedTemplateId: null,
		selectedCharacterId: null,
		userInfo: '',
		finalMessage: ''
	});

	// LocalStorage에서 로드
	if (typeof window !== 'undefined') {
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved) {
			try {
				const parsed = JSON.parse(saved);
				config = { ...config, ...parsed };
			} catch (e) {
				console.error('Failed to load AI config:', e);
			}
		}
	}

	// LocalStorage에 저장
	function save() {
		if (typeof window !== 'undefined') {
			localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
		}
	}

	return {
		get config() {
			return config;
		},
		setTemplate(id: number | null) {
			config.selectedTemplateId = id;
			save();
		},
		setCharacter(id: number | null) {
			config.selectedCharacterId = id;
			save();
		},
		setUserInfo(info: string) {
			config.userInfo = info;
			save();
		},
		setFinalMessage(message: string) {
			config.finalMessage = message;
			save();
		},
		reset() {
			config = {
				selectedTemplateId: null,
				selectedCharacterId: null,
				userInfo: '',
				finalMessage: ''
			};
			save();
		}
	};
}

export const aiConfigStore = createAIConfigStore();
