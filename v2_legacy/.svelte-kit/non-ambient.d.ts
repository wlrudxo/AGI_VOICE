
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/ai-settings" | "/ai-settings/characters" | "/ai-settings/chat-settings" | "/ai-settings/commands" | "/ai-settings/final-message" | "/ai-settings/system-messages" | "/ai-settings/user-info" | "/app-settings" | "/autonomous-driving" | "/autonomous-driving/manual-control" | "/autonomous-driving/settings" | "/autonomous-driving/triggers" | "/autonomous-driving/vehicle-control" | "/map-settings" | "/map-settings/generator" | "/map-settings/library" | "/map-settings/rag-test";
		RouteParams(): {
			
		};
		LayoutParams(): {
			"/": Record<string, never>;
			"/ai-settings": Record<string, never>;
			"/ai-settings/characters": Record<string, never>;
			"/ai-settings/chat-settings": Record<string, never>;
			"/ai-settings/commands": Record<string, never>;
			"/ai-settings/final-message": Record<string, never>;
			"/ai-settings/system-messages": Record<string, never>;
			"/ai-settings/user-info": Record<string, never>;
			"/app-settings": Record<string, never>;
			"/autonomous-driving": Record<string, never>;
			"/autonomous-driving/manual-control": Record<string, never>;
			"/autonomous-driving/settings": Record<string, never>;
			"/autonomous-driving/triggers": Record<string, never>;
			"/autonomous-driving/vehicle-control": Record<string, never>;
			"/map-settings": Record<string, never>;
			"/map-settings/generator": Record<string, never>;
			"/map-settings/library": Record<string, never>;
			"/map-settings/rag-test": Record<string, never>
		};
		Pathname(): "/" | "/ai-settings" | "/ai-settings/" | "/ai-settings/characters" | "/ai-settings/characters/" | "/ai-settings/chat-settings" | "/ai-settings/chat-settings/" | "/ai-settings/commands" | "/ai-settings/commands/" | "/ai-settings/final-message" | "/ai-settings/final-message/" | "/ai-settings/system-messages" | "/ai-settings/system-messages/" | "/ai-settings/user-info" | "/ai-settings/user-info/" | "/app-settings" | "/app-settings/" | "/autonomous-driving" | "/autonomous-driving/" | "/autonomous-driving/manual-control" | "/autonomous-driving/manual-control/" | "/autonomous-driving/settings" | "/autonomous-driving/settings/" | "/autonomous-driving/triggers" | "/autonomous-driving/triggers/" | "/autonomous-driving/vehicle-control" | "/autonomous-driving/vehicle-control/" | "/map-settings" | "/map-settings/" | "/map-settings/generator" | "/map-settings/generator/" | "/map-settings/library" | "/map-settings/library/" | "/map-settings/rag-test" | "/map-settings/rag-test/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.png" | "/svelte.svg" | "/tauri.svg" | "/vite.svg" | string & {};
	}
}