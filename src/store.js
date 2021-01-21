import Vue from 'vue'
import Vuex from 'vuex'

import * as urls from './urls.js';
import { globalState } from "./state";

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
    folders: [],
    tags: [],
  },

  mutations: {
    updateFolders(state, newFolders) {
      state.folders = newFolders;
    },
    updateTags(state, newTags) {
      state.tags = newTags;
    },
  },

  actions: {

    galleryRequest({commit}) {
      const metadata = JSON.parse(document.getElementById("gallery-metadata").textContent);
      commit("updateFolders", metadata.folders);
      commit("updateTags", metadata.tags);
      globalState.tags = metadata.tags;

      /*
      var xhr = new XMLHttpRequest();
      xhr.addEventListener("load", () => {
        if(xhr.status == 200) {
          var data = JSON.parse(xhr.response);
          commit("updateFolders", data.folders);
          commit("updateTags", data.tags);
          globalState.tags = data.tags;
        } else {
          //TODO: Error handling
        }
      });
      xhr.open("GET", urls.apiGallery);
      xhr.setRequestHeader("Accept", "application/json");
      xhr.send();
      */
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
        xhr.open("DELETE", urls.updateTags);
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
      xhr.open("POST", urls.updateTags);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      xhr.send(JSON.stringify(newTags));
    },

  },

  getters: {
    listFolders: (state) => (path) => {
      var foundFolders = [];
      var nParts = path == "" ? 0 : path.split("/").length;
      for(var candidate of state.folders) {
        var candidateParts = candidate.split("/");
        if(candidate.startsWith(path) && candidateParts.length == nParts+1) {
          foundFolders.push(candidateParts[candidateParts.length-1]);
        }
      }
      return foundFolders;
    },
  },

})
