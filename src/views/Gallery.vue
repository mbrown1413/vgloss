<template>
  <div class="gallery">

    <div class="gallery-tag-pane">
    </div>

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

    <FileDetailModal
      ref="fileDetailModal"
      @next="deltaModalItem(1)"
      @prev="deltaModalItem(-1)"
    />
  </div>
</template>

<style>
  .gallery {
    display: grid;
    grid-template-columns: [tag-pane-start] 200px [tag-pane-end gallery-grid-start] 1fr [gallery-grid-end];
    grid-template-rows: [action-pane-start tag-pane-start] min-content [action-pane-end gallery-grid-start] 1fr [gallery-grid-end detail-pane-start] min-content [detail-pane-end tag-pane-end];
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
  .gallery-tag-pane {
    grid-column: tag-pane-start / tag-pane-end;
    grid-row: tag-pane-start / tag-pane-end;
    border-right: black 2px solid;
  }
  .gallery-grid {
    grid-column: gallery-grid-start / gallery-grid-end;
    grid-row: gallery-grid-start / gallery-grid-end;
  }
  .gallery-detail-pane {
    grid-column: gallery-grid-start / gallery-grid-end;
    grid-row: detail-pane-start / detail-pane-end;
    background-color: #cccccc;
    border-top: black 2px solid;
    padding-top: 1em;
    padding-bottom: 1em;
  }
</style>

<script>
import GalleryGrid from '../GalleryGrid.vue';
import FileDetailModal from '../FileDetailModal.vue';
import * as urls from '../urls.js';

/* Remove extraneous "/" from beginning, middle and end. */
function trimSlashes(str) {
  return str.replace(/^\/+|\/+$/g, '').replace(/\/+/g, '/');
}

export default {
  name: 'Gallery',
  components: {
    GalleryGrid,
    FileDetailModal,
  },
  data() {
    return {
      selectedItems: [],
      items: [],
      folders: [],
      modalItem: null,
      modalDetails: null,
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
        request.addEventListener("load", this.onListApiResponse);
        request.open("GET", urls.fileList(queryParams));
        request.setRequestHeader("Accept", "application/json");
        request.send();
      },
      immediate: true,
    },

  },
  methods: {

    onListApiResponse(event) {
      var xhr = event.target;
      if(xhr.status == 200) {
        var data = JSON.parse(xhr.response);
        this.items = data.files;
        for(var item of this.items) {
          item.thumbnail = urls.fileThumbnail(item.hash);
        }
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
      } else {
        this.$refs.fileDetailModal.show(item);
      }
    },

    deltaModalItem(offset) {
      var current = this.$refs.fileDetailModal.file;
      var currentIndex = this.items.indexOf(current);
      var nextIndex = currentIndex + offset;
      if(currentIndex != -1 && nextIndex >= 0 && nextIndex < this.items.length) {
        var nextItem = this.items[nextIndex];
        if(nextItem.type != "folder") {
          this.$refs.fileDetailModal.show(this.items[nextIndex]);
        }
      }
    },

  },
}
</script>
