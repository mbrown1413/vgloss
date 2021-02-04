import cloneDeep from "lodash.clonedeep";
import debounce from "lodash.debounce";

import * as urls from '../urls.js';
import { apiRequest } from "../utils.js";


/* StateManager
 * Syncronizes state between backend and frontend.
 *
 * do(action) will call action.do(), mutating the client-side state. The action is put into a queue
 */
export default class StateManager {

  constructor(state) {
    this.state = state;
    this.actions = {
      pending: [],
      inFlight: [],
    };
    this.commitDebounced = debounce(this.commit, 3);
  }

  /* Perform action by calling action.do() and (eventually) perform the same
   * action on the backend. Action may be undone if it fails on the backend. */
  do(action) {
    this._performAction(action);
    this.actions.pending.push(action);
    this.maybeDelayedCommit();
  }

  _performAction(action) {
    // Read copy of state
    let newState = {}
    for(let stateName in action.constructor.stateNeeded) {
      newState[stateName] = cloneDeep(this.state[stateName]);
    }

    // Do action
    newState = action.do(newState);

    // Save copy of state
    for(let stateName in newState) {
      if(!action.constructor.stateNeeded.includes(stateName)) {
        console.error("State must be included in stateNeeded to be saved");
        continue;
      }
      this.state[stateName] = newState[stateName];
    }
  }

  maybeDelayedCommit() {
    if(this.actions.pending.length && !this.actions.inFlight.length) {
      this.commitDebounced();
    }
  }

  async commit() {
    if(!this.actions.pending) {
      return;
    }
    if(this.actions.inFlight.length) {
      // We'll detect pending actions when in-flight actions are finished
      return;
    }

    // Move actions to pending
    this.actions.inFlight = this.actions.pending;
    this.actions.pending = [];

    // Send request to perform actions on backend
    let data = this.actions.inFlight.map(a => a.serialize());
    try {
      await apiRequest("POST", urls.action, data);
    } catch(e) {
      //TODO: Error handling
    }

    this.actions.inFlight = [];
    this.maybeDelayedCommit();
  }

}
