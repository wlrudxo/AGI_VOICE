// @ts-nocheck
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = async () => {
	// Redirect to chat-settings as the default AI settings page
	throw redirect(302, '/ai-settings/chat-settings');
};
;null as any as PageServerLoad;