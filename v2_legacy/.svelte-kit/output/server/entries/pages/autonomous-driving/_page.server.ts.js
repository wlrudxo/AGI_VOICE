import { redirect } from "@sveltejs/kit";
const load = async () => {
  throw redirect(302, "/autonomous-driving/vehicle-control");
};
export {
  load
};
