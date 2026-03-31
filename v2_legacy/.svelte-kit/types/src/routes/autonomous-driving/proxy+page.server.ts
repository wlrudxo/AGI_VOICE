// @ts-nocheck
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = async () => {
	// Redirect to vehicle-control as the default autonomous driving page
	throw redirect(302, '/autonomous-driving/vehicle-control');
};
;null as any as PageServerLoad;