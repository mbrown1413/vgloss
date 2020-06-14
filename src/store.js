import Vue from 'vue'
import Vuex from 'vuex'

import * as urls from './urls.js';

Vue.use(Vuex)

export default new Vuex.Store({

  state: {
    folderTree: {},
  },
  mutations: {
    updateFolderTree(state, newFolderTree) {
      state.folderTree = newFolderTree;
    },
  },
  actions: {
    galleryRequest({commit}) {
      var xhr = new XMLHttpRequest();
      xhr.addEventListener("load", () => {
        if(xhr.status == 200) {
          var data = JSON.parse(xhr.response);
          commit("updateFolderTree", data.folderTree);
        } else {
          //TODO: Error handling
        }
      });
      xhr.open("GET", urls.apiGallery());
      xhr.setRequestHeader("Accept", "application/json");
      xhr.send();
    },
  },
  getters: {
    listFolders: (state) => (path) => {
      var dirNode = state.folderTree;
      for(var folder of path.split("/")) {
        if(!folder.length) continue
        dirNode = dirNode[folder];
        if(dirNode === undefined) {
          return [];
        }
      }
      return Object.keys(dirNode);
    },
  },
})
