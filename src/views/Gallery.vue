<template>
  <div class="gallery">

    <GalleryGrid
      :items="items"
      :selectedItems="selectedItems"
      v-model="selectedItems"
      @doubleClick="onItemDoubleClick"
    />

    <div
      class="gallery-detail-pane"
    >
        <div v-if="selectedItems">
          {{ selectedItems.join(" | ") }}
        </div>

        <div>
          Current Folder:
          <span v-for="(part, i) in folderPath" :key="i">
            <router-link v-if="i < folderPath.length-1" :to="part.link">{{ part.name }}</router-link>
            <template v-else>{{ part.name }}</template>
            <template v-if="i < folderPath.length-1">
              /
            </template>
          </span>
        </div>
    </div>

  </div>
</template>

<style>
  .gallery {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: 1fr min-content;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
  .gallery-detail-pane {
    background-color: #cccccc;
    border-top: black 2px solid;
    padding-top: 1em;
    padding-bottom: 1em;
  }
</style>

<script>
import GalleryGrid from '../GalleryGrid.vue';

/* Remove extraneous "/" from beginning, middle and end. */
function trimSlashes(str) {
  return str.replace(/^\/+|\/+$/g, '').replace(/\/+/g, '/');
}

export default {
  name: 'Gallery',
  components: {
    "GalleryGrid": GalleryGrid,
  },
  data() {
    return {
      selectedItems: [],
      items: [],
      folders: [],
    };
  },
  computed: {

    thisFolder() {
      var folder = this.$route.params.pathMatch;
      return folder === undefined ? null : trimSlashes(folder)+"/";
    },

    queryParams() {
      return {
        folder: this.thisFolder,
      };
    },

    folderPath() {
      if(!this.thisFolder) {
        return [];
      } else {
        var pathParts = [{name: "home", link: "/gallery/folder/"}];
        for(var part of trimSlashes(this.thisFolder).split("/")) {
          if(part == "") continue;
          pathParts.push({
            name: part,
            link: pathParts[pathParts.length-1].link + part + "/",
          })
        }
        return pathParts;
      }
    },

  },
  watch: {

    queryParams: {
      handler(queryParams) {
        // Make API request
        var request = new XMLHttpRequest();
        request.addEventListener("load", this.onApiResponse);
        var paramString = "";
        for(var param in queryParams) {
          if(queryParams[param] !== null) {
            paramString += `${param}=${encodeURIComponent(queryParams[param])}`;
          }
        }
        request.open("GET", "/api/gallery/query?"+paramString);
        request.setRequestHeader("Accept", "application/json");
        request.send();
      },
      immediate: true,
    },

  },
  methods: {

    onApiResponse(event) {
      var xhr = event.target;
      if(xhr.status == 200) {
        var data = JSON.parse(xhr.response);
        this.items = data.files;
        for(var folder of data.folders.reverse()) {
          this.items.unshift({
            type: "folder",
            name: folder,
            thumbnail: "/img/folder.svg",
          })
        }
      } else {
        //TODO: Error Handling
      }
    },

    subFolderLink(folder) {
      return "/gallery/folder/" + this.thisFolder + trimSlashes(folder);
    },

    onItemDoubleClick(item) {
      if(item.type == "folder") {
        this.$router.push(this.subFolderLink(item.name));
      }
    },

  },
}
</script>
