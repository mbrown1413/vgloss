<template>
  <div class="gallery">

    <div class="gallery-filter-pane">
      <h4 style="margin-left: 0.25em">Folders</h4>
      <FolderFilterTree
        :tree="folderTree"
        :selected="[selectedFolder]"
        @change="onFolderSelect"
      />

      <!--
      <hr>
      <h4>Tags</h4>
      <FolderFilterTree />
      -->
    </div>

    <div class="gallery-action-pane">
      <span v-for="(part, i) in folderPath" :key="i">
        <router-link v-if="i < folderPath.length-1" :to="part.url">{{ part.name }}</router-link>
        <template v-else>{{ part.name }}</template>
        <template v-if="i < folderPath.length-1">
          /
        </template>
      </span>
    </div>

    <GalleryGrid
      :items="gridItems"
      :selectedItems="selectedItems"
      v-model="selectedItems"
      @doubleClick="onItemDoubleClick"
    />

    <div
      class="gallery-info-pane"
    >
        <div v-if="selectedItems">
          {{ selectedItems.join(" | ") }}
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
    grid-template-columns: [filter-pane-start] 200px [filter-pane-end gallery-grid-start] 1fr [gallery-grid-end];
    grid-template-rows: [action-pane-start filter-pane-start] min-content [action-pane-end gallery-grid-start] 1fr [gallery-grid-end info-pane-start] min-content [info-pane-end filter-pane-end];
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
  .gallery-filter-pane {
    grid-column: filter-pane-start / filter-pane-end;
    grid-row: filter-pane-start / filter-pane-end;
    border-right: black 2px solid;
  }
  .gallery-action-pane {
    grid-column: gallery-grid-start / gallery-grid-end;
    grid-row: action-pane-start / action-pane-end;
    border-bottom: black 2px solid;
  }
  .gallery-info-pane {
    grid-column: gallery-grid-start / gallery-grid-end;
    grid-row: info-pane-start / info-pane-end;
    border-top: black 2px solid;
  }
  .gallery-action-pane, .gallery-info-pane {
    background-color: #cccccc;
    padding: 0.5em;
  }
  .gallery-grid {
    grid-column: gallery-grid-start / gallery-grid-end;
    grid-row: gallery-grid-start / gallery-grid-end;
  }
</style>

<script>
import GalleryGrid from '../GalleryGrid.vue';
import FolderFilterTree from '../FolderFilterTree.vue';
import FileDetailModal from '../FileDetailModal.vue';
import * as urls from '../urls.js';

/* Gallery URLs
 * All data that determines which items are shown will be present in the URL.
 * This ensures the current location can always be bookmarked. This data is
 * available as a computed property, so it cannot be changed directly. Instead,
 * change the URL and the computed properties will update accordingly.
 */
export default {
  name: 'Gallery',
  components: {
    GalleryGrid,
    FolderFilterTree,
    FileDetailModal,
  },
  data() {
    return {
      files: [],
      selectedItems: [],
      modalItem: null,
      modalDetails: null,
    };
  },
  mounted() {
    this.$store.dispatch("galleryRequest");
  },
  computed: {

    folderTree() {
      return this.$store.state.folderTree;
    },

    selectedFolder() {
      var folder = this.$route.params.pathMatch;
      return folder || "";
    },

    queryParams() {
      return {
        folder: this.selectedFolder,
      };
    },

    folderPath() {
      return urls.folderListFromPath(this.selectedFolder);
    },

    gridItems() {
      var items = [];

      // Folders
      var folders = this.$store.getters.listFolders(this.selectedFolder);
      for(var folder of folders) {
        items.push({
          type: "folder",
          name: folder,
          path: this.selectedFolder + "/" + folder,
          thumbnail: "/img/folder.svg",
        });
      }

      // Files
      for(var file of this.files) {
        file.thumbnail = urls.fileThumbnail(file.hash);
        items.push(file);
      }

      return items;
    },

  },
  watch: {

    queryParams: {
      handler(queryParams) {
        // Make API request
        var request = new XMLHttpRequest();
        request.addEventListener("load", (event) => {
          var xhr = event.target;
          if(xhr.status == 200) {
            this.files = JSON.parse(xhr.response);
          } else {
            //TODO: Error Handling
          }
        });
        request.open("GET", urls.apiFileList(queryParams));
        request.setRequestHeader("Accept", "application/json");
        request.send();
      },
      immediate: true,
      deep: true,
    },

  },
  methods: {

    onItemDoubleClick(item) {
      if(item.type == "folder") {
        this.$router.push(urls.gallery(item.path));
      } else {
        this.$refs.fileDetailModal.show(item);
      }
    },

    onFolderSelect(selectedFolders) {
      if(selectedFolders.length == 0) {
        this.$router.push(urls.gallery(""));
      } else if(selectedFolders.length == 1) {
        this.$router.push(urls.gallery(selectedFolders[0]));
      }
    },

    deltaModalItem(offset) {
      var current = this.$refs.fileDetailModal.file;
      var currentIndex = this.gridItems.indexOf(current);
      var nextIndex = currentIndex + offset;
      if(currentIndex != -1 && nextIndex >= 0 && nextIndex < this.gridItems.length) {
        var nextItem = this.gridItems[nextIndex];
        if(nextItem.type != "folder") {
          this.$refs.fileDetailModal.show(this.gridItems[nextIndex]);
        }
      }
    },

  },
}
</script>
