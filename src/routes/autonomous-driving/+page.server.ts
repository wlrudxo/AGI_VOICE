import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Redirect to vehicle-control as the default autonomous driving page
	throw redirect(302, '/autonomous-driving/vehicle-control');
};
