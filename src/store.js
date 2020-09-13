import Vue from 'vue'
import Vuex from 'vuex'

import * as urls from './urls.js';

Vue.use(Vuex)

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

export default new Vuex.Store({

  state: {
    folderTree: {},
    tags: [],
  },

  mutations: {
    updateFolderTree(state, newFolderTree) {
      state.folderTree = newFolderTree;
    },
    updateTags(state, newTags) {
      state.tags = newTags;
    },

  },

  actions: {

    galleryRequest({commit}) {
      var xhr = new XMLHttpRequest();
      xhr.addEventListener("load", () => {
        if(xhr.status == 200) {
          var data = JSON.parse(xhr.response);
          commit("updateFolderTree", data.folderTree);
          commit("updateTags", data.tags);
        } else {
          //TODO: Error handling
        }
      });
      xhr.open("GET", urls.apiGallery());
      xhr.setRequestHeader("Accept", "application/json");
      xhr.send();
    },

    saveTags({commit}, newTags) {
      // Find deleted tags
      var stillPresentTagIds = new Set(newTags.map(tag => tag.id));
      var deleteData = [];
      for(var tag of this.state.tags) {
        if(!stillPresentTagIds.has(tag.id)) {
          deleteData.push({id: tag.id});
        }
      }

      // Delete
      if(deleteData.length > 0) {
        var xhr = new XMLHttpRequest();
        xhr.addEventListener("load", () => {
          if(xhr.status != 200) {
            //TODO: Error handling
          }
        });
        xhr.open("DELETE", urls.updateTags());
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        xhr.send(JSON.stringify(deleteData));
      }

      // Create / Update
      xhr = new XMLHttpRequest();
      xhr.addEventListener("load", () => {
        if(xhr.status == 200) {
          var data = JSON.parse(xhr.response);
          commit("updateTags", data);
        } else {
          //TODO: Error handling
        }
      });
      xhr.open("POST", urls.updateTags());
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      xhr.send(JSON.stringify(newTags));
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
