export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.png","svelte.svg","tauri.svg","vite.svg"]),
	mimeTypes: {".png":"image/png",".svg":"image/svg+xml"},
	_: {
		client: {start:"_app/immutable/entry/start.BpRHgeJR.js",app:"_app/immutable/entry/app.BhUCyKPL.js",imports:["_app/immutable/entry/start.BpRHgeJR.js","_app/immutable/chunks/DGe9RVYM.js","_app/immutable/chunks/DoRbC73M.js","_app/immutable/chunks/BL0wSOjl.js","_app/immutable/chunks/CehuOInK.js","_app/immutable/entry/app.BhUCyKPL.js","_app/immutable/chunks/BL0wSOjl.js","_app/immutable/chunks/DoRbC73M.js","_app/immutable/chunks/Bzak7iHL.js","_app/immutable/chunks/D_XkNnm9.js","_app/immutable/chunks/CehuOInK.js","_app/immutable/chunks/RI3GwsiT.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js')),
			__memo(() => import('./nodes/6.js')),
			__memo(() => import('./nodes/7.js')),
			__memo(() => import('./nodes/8.js')),
			__memo(() => import('./nodes/9.js')),
			__memo(() => import('./nodes/10.js')),
			__memo(() => import('./nodes/11.js')),
			__memo(() => import('./nodes/12.js')),
			__memo(() => import('./nodes/13.js')),
			__memo(() => import('./nodes/14.js')),
			__memo(() => import('./nodes/15.js')),
			__memo(() => import('./nodes/16.js')),
			__memo(() => import('./nodes/17.js')),
			__memo(() => import('./nodes/18.js')),
			__memo(() => import('./nodes/19.js')),
			__memo(() => import('./nodes/20.js')),
			__memo(() => import('./nodes/21.js')),
			__memo(() => import('./nodes/22.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 5 },
				endpoint: null
			},
			{
				id: "/ai-settings",
				pattern: /^\/ai-settings\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 6 },
				endpoint: null
			},
			{
				id: "/ai-settings/characters",
				pattern: /^\/ai-settings\/characters\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 7 },
				endpoint: null
			},
			{
				id: "/ai-settings/chat-settings",
				pattern: /^\/ai-settings\/chat-settings\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 8 },
				endpoint: null
			},
			{
				id: "/ai-settings/commands",
				pattern: /^\/ai-settings\/commands\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 9 },
				endpoint: null
			},
			{
				id: "/ai-settings/final-message",
				pattern: /^\/ai-settings\/final-message\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 10 },
				endpoint: null
			},
			{
				id: "/ai-settings/system-messages",
				pattern: /^\/ai-settings\/system-messages\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 11 },
				endpoint: null
			},
			{
				id: "/ai-settings/user-info",
				pattern: /^\/ai-settings\/user-info\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 12 },
				endpoint: null
			},
			{
				id: "/app-settings",
				pattern: /^\/app-settings\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 13 },
				endpoint: null
			},
			{
				id: "/autonomous-driving",
				pattern: /^\/autonomous-driving\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 14 },
				endpoint: null
			},
			{
				id: "/autonomous-driving/manual-control",
				pattern: /^\/autonomous-driving\/manual-control\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 15 },
				endpoint: null
			},
			{
				id: "/autonomous-driving/settings",
				pattern: /^\/autonomous-driving\/settings\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 16 },
				endpoint: null
			},
			{
				id: "/autonomous-driving/triggers",
				pattern: /^\/autonomous-driving\/triggers\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 17 },
				endpoint: null
			},
			{
				id: "/autonomous-driving/vehicle-control",
				pattern: /^\/autonomous-driving\/vehicle-control\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 18 },
				endpoint: null
			},
			{
				id: "/map-settings",
				pattern: /^\/map-settings\/?$/,
				params: [],
				page: { layouts: [0,4,], errors: [1,,], leaf: 19 },
				endpoint: null
			},
			{
				id: "/map-settings/generator",
				pattern: /^\/map-settings\/generator\/?$/,
				params: [],
				page: { layouts: [0,4,], errors: [1,,], leaf: 20 },
				endpoint: null
			},
			{
				id: "/map-settings/library",
				pattern: /^\/map-settings\/library\/?$/,
				params: [],
				page: { layouts: [0,4,], errors: [1,,], leaf: 21 },
				endpoint: null
			},
			{
				id: "/map-settings/rag-test",
				pattern: /^\/map-settings\/rag-test\/?$/,
				params: [],
				page: { layouts: [0,4,], errors: [1,,], leaf: 22 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
