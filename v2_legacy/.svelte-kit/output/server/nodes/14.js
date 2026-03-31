import * as server from '../entries/pages/autonomous-driving/_page.server.ts.js';

export const index = 14;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/autonomous-driving/_page.svelte.js')).default;
export { server };
export const server_id = "src/routes/autonomous-driving/+page.server.ts";
export const imports = ["_app/immutable/nodes/14.BUSfeChB.js","_app/immutable/chunks/Bzak7iHL.js","_app/immutable/chunks/Dns8sIju.js","_app/immutable/chunks/BL0wSOjl.js"];
export const stylesheets = ["_app/immutable/assets/14.BFAgXczA.css"];
export const fonts = [];
