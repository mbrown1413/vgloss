
import { apiFileList } from "../urls.js";
import { apiRequest } from "../utils.js";

export async function queryFileList(params) {
  let response = await apiRequest("GET", apiFileList(params));
  return response.json();
}
