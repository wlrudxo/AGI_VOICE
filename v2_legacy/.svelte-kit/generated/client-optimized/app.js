export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17'),
	() => import('./nodes/18'),
	() => import('./nodes/19'),
	() => import('./nodes/20'),
	() => import('./nodes/21'),
	() => import('./nodes/22')
];

export const server_loads = [];

export const dictionary = {
		"/": [5],
		"/ai-settings": [~6,[2]],
		"/ai-settings/characters": [7,[2]],
		"/ai-settings/chat-settings": [8,[2]],
		"/ai-settings/commands": [9,[2]],
		"/ai-settings/final-message": [10,[2]],
		"/ai-settings/system-messages": [11,[2]],
		"/ai-settings/user-info": [12,[2]],
		"/app-settings": [13],
		"/autonomous-driving": [~14,[3]],
		"/autonomous-driving/manual-control": [15,[3]],
		"/autonomous-driving/settings": [16,[3]],
		"/autonomous-driving/triggers": [17,[3]],
		"/autonomous-driving/vehicle-control": [18,[3]],
		"/map-settings": [19,[4]],
		"/map-settings/generator": [20,[4]],
		"/map-settings/library": [21,[4]],
		"/map-settings/rag-test": [22,[4]]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.js';