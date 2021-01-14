import Vue from 'vue'

import StateManager from "./manager.js";

/* All global state sync'd with the backend. All values are observable and vue
 * components are intended to observe them, but not mutate them directly. If
 * you need to mutate this state, perform an action using doAction(). */
export var globalState = Vue.observable({
  tags: Vue.observable([]),
  folders: Vue.observable([]),
});

export var stateManager = new StateManager(globalState);

/* Shortcut for performing an action on the global state manager. */
export function doAction(action) {
  stateManager.do(action);
}
