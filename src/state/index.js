import Vue from 'vue'

import StateManager from "./manager.js";

/* All global state sync'd with the backend. All values are observable and vue
 * components are intended to observe them, but not mutate them directly. If
 * you need to mutate this state, perform an action using doAction(). */
export var globalState = Vue.observable({
  tags: Vue.observable([]),
  folders: Vue.observable([]),
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
