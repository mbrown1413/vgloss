import Vue from 'vue'

import App from './App.vue'
import router from './router'
import { globalState, stateManager } from "./state";

Vue.config.productionTip = false

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')

/* Shortcut access to state from debugger */
window._debug = {
  globalState,
  stateManager,
}
