<template>
  <div class="gallery">

    <div class="gallery-filter-pane">
      <h4 style="margin-left: 0.25em">Folders</h4>
      <Tree
        :items="folderItems"
        :selectedIds="[selectedFolder]"
        @change-selected="onFolderSelect"
      />

      <hr>
      <h4 style="margin-left: 0.25em">
        Tags <small>(<a href="#" @click.prevent="$refs.tagEditModal.show()">edit</a>)</small>
      </h4>
      <Tree
        :items="tagItems"
        :multiSelect="true"
        :autoSelectRelated="true"
        v-model="filteringTags"
      />
    </div>

    <div class="gallery-action-pane">
      <span v-for="(part, i) in folderPath" :key="i">
        <router-link v-if="i < folderPath.length-1" :to="part.url">{{ part.name }}</router-link>
        <template v-else>{{ part.name }}</template>
        <template v-if="i < folderPath.length-1">
          /
        </template>
      </span>
      <div class="dropdown">
        <button
          class="btn btn-secondary dropdown-toggle"
          :disabled="selectedItems.length == 0"
          type="button"
          id="dropdownMenuButton"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          Apply Tags
        </button>
        <div
          class="dropdown-menu"
          aria-labelledby="dropdownMenuButton"
          @click="$event.stopPropagation()"
        >
          <Tree
            :items="tagItems"
            :multiSelect="true"
            :selectedIds="selectedItemTags"
            @change-selected="onFileTagChange"
          />
        </div>
      </div>
    </div>

    <GalleryGrid
      :items="gridItems"
      :selectedItems="selectedItems"
      v-model="selectedItems"
      @double-click="onItemDoubleClick"
    />

    <div
      class="gallery-info-pane"
    >
      <div v-if="selectedItems">
        {{ selectedItems.join(" | ") }}
      </div>
    </div>

    <!-- Modals -->
    <FileDetailModal
      ref="fileDetailModal"
      @next="deltaModalItem(1)"
      @prev="deltaModalItem(-1)"
    />
    <TagEditModal ref="tagEditModal" />
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
import GalleryGrid from './GalleryGrid.vue';
import Tree from '../Tree.vue';
import FileDetailModal from './FileDetailModal.vue';
import TagEditModal from './TagEditModal.vue';
import { getCookie } from "../utils.js";
import * as urls from '../urls.js';
import { globalState, listFolders } from "../state";

import 'bootstrap/js/dist/dropdown';

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
    Tree,
    FileDetailModal,
    TagEditModal,
  },
  data() {
    return {
      files: [],
      filteringTags: [],
      selectedItems: [],
      modalItem: null,
      modalDetails: null,
    };
  },
  computed: {

    filesByName() {
      var filesByName = {};
      for(var file of this.files) {
        filesByName[file.name] = file;
      }
      return filesByName;
    },

    folderItems() {
      var items = [{
        id: "",
        text: "Root",
        parent: null,
      }];
      for(var path of globalState.folders) {
        var lastSlashIdx = path.lastIndexOf("/");
        items.push({
          id: path,
          text: path.slice(lastSlashIdx+1),
          parent: lastSlashIdx == -1 ? "" : path.slice(0, lastSlashIdx),
        });
      }
      return items;
    },

    selectedFolder() {
      var folder = this.$route.params.pathMatch;
      return folder || "";
    },

    tagItems() {
      var items = [];
      for(var tag of globalState.tags) {
        items.push({
          id: tag.id,
          text: tag.name,
          parent: tag.parent,
        });
      }
      return items;
    },

    queryParams() {
      return {
        folder: this.selectedFolder,
        tag: this.filteringTags.join(","),
      };
    },

    folderPath() {
      return urls.folderListFromPath(this.selectedFolder);
    },

    gridItems() {
      var items = [];

      // Folders
      for(var folder of listFolders(this.selectedFolder)) {
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

    selectedItemTags() {
      // Update current file tags based on the selected files.
      // For now, we only consider our selection to have at tag if every item
      // in the selection has the tag.
      var selected = new Set();

      // Two pass algorithm
      // 1) add tags from all selected files
      for(var item of this.selectedItems) {
        var itemTags = this.filesByName[item] ? this.filesByName[item].tags : [];
        for(var tag of itemTags) {
          selected.add(tag);
        }
      }

      // 2) remove tags not in selected files
      for(item of this.selectedItems) {
        itemTags = this.filesByName[item] ? this.filesByName[item].tags : [];
        for(tag of selected) {
          if(!itemTags.includes(tag)) {
            selected.delete(tag);
          }
        }
      }

      return [...selected];
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

    onFileTagChange(newSelectedTags) {
      var oldSelectedTags = this.selectedItemTags;

      var newSet = new Set(newSelectedTags);
      var oldSet = new Set(oldSelectedTags);
      var addedTags   = newSelectedTags.filter(t => !oldSet.has(t));
      var deletedTags = oldSelectedTags.filter(t => !newSet.has(t));

      this.addFileTags(this.selectedItems, addedTags);
      this.deleteFileTags(this.selectedItems, deletedTags);
    },

    addFileTags(itemNames, tagIds) {
      this._editFileTags(itemNames, tagIds, true);
    },

    deleteFileTags(itemNames, tagIds) {
      this._editFileTags(itemNames, tagIds, false);
    },

    _editFileTags(itemNames, tagIds, _add) {
      var data = [];

      // Frontend edit
      for(var tagId of tagIds) {
        for(var name of itemNames) {
          var fileInfo = this.filesByName[name];
          if(!fileInfo) continue

          var neededEdit = false;
          if(_add && !fileInfo.tags.includes(tagId)) {
            fileInfo.tags.push(tagId);
            neededEdit = true;
          } else if(!_add && fileInfo.tags.includes(tagId)) {
            fileInfo.tags.splice(fileInfo.tags.indexOf(tagId), 1);
            neededEdit = true;
          }

          if(neededEdit) {
            data.push({file: fileInfo.hash, tag: tagId});
          }
        }
      }

      if(data.length === 0) {
        return;
      }

      // Backend edit request
      var xhr = new XMLHttpRequest();
      xhr.addEventListener("load", () => {
        if(![200, 204].includes(xhr.status)) {
          //TODO: Error handling
          // Undo on the frontend the edit that failed on the backend
          for(var dataItem of data) {
            fileInfo = this.files.find(f => f.hash === dataItem.file);
            if(_add) {
              fileInfo.tags.splice(fileInfo.tags.indexOf(data.tag), 1);
            } else {
              fileInfo.tags.push(data.tag);
            }
          }
        }
      });
      xhr.open(_add ? "POST" : "DELETE", urls.fileTags);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      xhr.send(JSON.stringify(data));
    },

  },
}
</script>
