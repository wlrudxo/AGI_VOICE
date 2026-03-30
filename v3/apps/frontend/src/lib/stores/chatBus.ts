import { writable } from 'svelte/store';

export interface TriggerChatMessageEvent {
	type: 'system' | 'llm_response' | 'error';
	triggerName: string;
	content: string;
}

interface SelectionRequest {
	id: number | null;
	version: number;
}

interface TriggerEventState {
	event: TriggerChatMessageEvent | null;
	version: number;
}

const conversationSelection = writable<SelectionRequest>({ id: null, version: 0 });
const conversationListVersion = writable(0);
const chatSettingsVersion = writable(0);
const triggerChatEvent = writable<TriggerEventState>({ event: null, version: 0 });

export const chatBus = {
	conversationSelection,
	conversationListVersion,
	chatSettingsVersion,
	triggerChatEvent,

	selectConversation(id: number | null) {
		conversationSelection.update((state) => ({ id, version: state.version + 1 }));
	},

	notifyConversationChanged() {
		conversationListVersion.update((value) => value + 1);
	},

	notifyChatSettingsUpdated() {
		chatSettingsVersion.update((value) => value + 1);
	},

	pushTriggerEvent(event: TriggerChatMessageEvent) {
		triggerChatEvent.update((state) => ({ event, version: state.version + 1 }));
	}
};
