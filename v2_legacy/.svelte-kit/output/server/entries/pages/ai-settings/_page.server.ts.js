import { redirect } from "@sveltejs/kit";
const load = async () => {
  throw redirect(302, "/ai-settings/chat-settings");
};
export {
  load
};
