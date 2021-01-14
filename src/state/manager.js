import cloneDeep from "lodash.clonedeep";
import debounce from "lodash.debounce";

import * as urls from '../urls.js';


export function getCookie(name) {
  // https://docs.djangoproject.com/en/3.1/ref/csrf/#ajax
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
  }
  return null;
}


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

    // Make request
    var xhr = new XMLHttpRequest();
    xhr.addEventListener("load", () => {
      if(xhr.status != 200) {
        //TODO: Error handling
        return;
      }
      // Detect if there are new pending actions
      this.maybeDelayedCommit();
    })
    xhr.open("POST", urls.action);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.send(JSON.stringify(
      this.actions.pending.map(a => a.serialize())
    ));

    // Move actions to pending
    this.actions.inFlight = this.actions.pending;
    this.actions.pending = [];
  }

}
