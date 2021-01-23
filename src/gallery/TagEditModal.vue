<template>
  <b-modal
    ref="modal"
    title="Edit Tags"
    centered
    hide-header-close
    no-close-on-backdrop
    size="xl"
  >

    <template v-slot:modal-footer>
      <div style="position: absolute; left: 0;">
        <button
          class="float-right ml-3 btn btn-danger"
          @click="deleteTag(selectedTag.id)"
          :disabled="selectedTag == null"
        >-</button>
        <button
          class="float-right ml-5 btn btn-success"
          @click="addTag"
        >+</button>
      </div>

      <button
        type="button"
        class="btn btn-secondary"
        @click="onCancel"
      >
        Cancel
      </button>
      <button
        type="button"
        class="btn btn-primary"
        @click="onSave"
      >
        Save
      </button>
    </template>

    <div class="container">
      <div class="row">
        <div class="col-3">

          <Tree
            ref="tree"
            :items="treeData"
            v-model="selectedIds"
          />

        </div>
        <div class="col-9" v-if="selectedTag">

          <h5>{{ selectedTagPath.map(tag => tag.text).join(" &rarr; ") }}</h5>
          <div class="mt-3 input-group">
            <div class="input-group-prepend">
              <label class="input-group-text" for="tagEditor-tag-name">
                Name
              </label>
            </div>
            <input v-model="selectedTag.name" class="form-control" id="tagEditor-tag-name">
          </div>

          <div class="mt-3 input-group">
            <div class="input-group-prepend">
              <label class="input-group-text" for="tagEditor-tag-parent">
                Parent
              </label>
            </div>
            <select v-model="selectedTag.parent" class="form-control" id="tagEditor-tag-parent">
              <option :value="null">(Root)</option>
              <option
                v-for="{tag, depth, disabled} in parentOptions"
                :key="tag.id"
                :value="tag.id"
                :disabled="disabled"
                v-html="'&nbsp;'.repeat(4+depth*4) + tag.text"
              >
              </option>
            </select>
          </div>

        </div>
      </div>
    </div>
  </b-modal>
</template>

<style>
@import "~tree-component/dist/tree.css";
</style>

<script>
import { BModal } from "bootstrap-vue/esm/components/modal/modal";

import { globalState } from "../state";
import Tree from "../Tree.vue";
import { doAction } from "../state"
import * as actions from "../actions"

/* TagEditModal
 * Edit tree of tags.
 *
 * When opening the modal, `tags` is populated with the current tags objects.
 * This is edited as a local copy, and only saved when the "Save" button is
 * pressed.
 */
export default {
  name: "TagEditModal",
  components: {
    BModal,
    Tree,
  },
  data() {
    return {
      tags: {},  // Map tag ID to tag object
      selectedIds: [],
    };
  },
  computed: {

    selectedId() {
      return this.selectedIds.length == 0 ? null : this.selectedIds[0];
    },

    selectedTag() {
      return this.tags[this.selectedId] || null;
    },

    selectedTagPath() {
      return [...this.$refs.tree.getItemPath(this.selectedId)];
    },

    treeData() {
      var items = [];
      for(var tag of Object.values(this.tags)) {
        items.push({
          id: tag.id,
          text: tag.name,
          parent: tag.parent,
        });
      }
      return items;
    },

    /* Dropdown options for the selected tag's parent. */
    parentOptions() {
      var disabledIds = new Set([this.selectedId]);
      for(var item of this.$refs.tree.getDescendantItems(this.selectedId)) {
        disabledIds.add(item.id);
      }

      var options = [];
      for(var visit of this.$refs.tree.walkTree()) {
        options.push({
          tag: visit.item,
          depth: visit.depth,
          disabled: disabledIds.has(visit.id),
        });
      }
      return options;
    },

  },
  methods: {

    show() {
      // Convert tag list to mapping from tag ID
      var tagList = JSON.parse(JSON.stringify(globalState.tags));
      this.tags = {};
      for(var tag of tagList) {
        this.$set(this.tags, tag.id, tag);
      }

      this.tempCounter = 0;
      this.select(null)
      this.$refs.modal.show();
    },

    select(tagId) {
      this.selectedIds = tagId == null ? [] : [tagId];
    },

    onCancel() {
      this.$refs.modal.hide()
    },

    onSave() {
      doAction(new actions.TagUpdate(
        Object.values(this.tags)
      ))
      this.$refs.modal.hide()
    },

    addTag() {
      // Generate temporary ID for new tag.
      // Since we can't have a permenant ID until the tag is saved to the
      // database, we reference by a temporary ID which the backend will
      // convert to a real ID when we save.
      var newId = "temp" + this.tempCounter;
      this.tempCounter++;

      this.$set(this.tags, newId, {
        id: newId,
        name: "New Tag "+this.tempCounter,
        parent: this.selectedTag === null ? null : this.selectedTag.parent,
      });
      this.select(newId);
    },

    deleteTag(tagId) {
      this.$delete(this.tags, tagId);
      if(this.selectedId == tagId) {
        this.select(null);
      }

      for(var item of this.$refs.tree.getDescendantItems(tagId)) {
        this.$delete(this.tags, item.id);
        if(this.selectedId == item.id) {
          this.select(null);
        }
      }
    },

  },
}
</script>
