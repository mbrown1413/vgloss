/* State
 * A central place that stores all state retrieved from the backend.
 *
 * Here are the places state is stored in the frontend:
 *
 *   * UI state: Which file is selected? is the modal open? This kind of data
 *     is just temporary and is never stored in the backend. It is stored in
 *     individual vue components.
 *
 *   * global state: Stored in the `globalState` vue observable in this
 *     package. This state is a reflection of the ground truth of the backend
 *     database. Components should be careful mutating `globalState` directly.
 *     Most of the time it's more appropriate to instead create an `Action`
 *     instance and perform the action by calling `doAction()`.
 *
 *   * caching: Some queries may cache data to prevent unneeded calls to the
 *     backend.
 *
 * An overview of the mechanisms for mutating and retrieving state:
 *
 *   * Actions: Actions mutate the shared state between frontend and backend.
 *     See actions.js for details.
 *
 *   * Queries: Queries are frontend requests for information stored the
 *     backend. Query functions start with "query" and return a promise which
 *     may be rejected with an error message.
 */
import Vue from 'vue';

import StateManager from "./manager.js";

/* All global state sync'd with the backend. All values are observable and vue
 * components are intended to observe them, but not mutate them directly. If
 * you need to mutate this state, perform an action using doAction(). */
export var globalState = Vue.observable({
  // These vars hold complete state of backend for their respective values.
  tags: Vue.observable([]),
  folders: Vue.observable([]),

  // These vars hold a subset of backend state
  files: Vue.observable([]),
});

function readStateFromPage() {
  const metadata = JSON.parse(document.getElementById("gallery-metadata").textContent);
  globalState.tags = metadata.tags;
  globalState.folders = metadata.folders
}
readStateFromPage();

export var stateManager = new StateManager(globalState);

/* Shortcut for performing an action on the global state manager. */
export function doAction(action) {
  stateManager.do(action);
}

export function listFolders(path) {
  var foundFolders = [];
  var nParts = path == "" ? 0 : path.split("/").length;
  for(var candidate of globalState.folders) {
    var candidateParts = candidate.split("/");
    if(candidate.startsWith(path) && candidateParts.length == nParts+1) {
      foundFolders.push(candidateParts[candidateParts.length-1]);
    }
  }
  return foundFolders;
}
