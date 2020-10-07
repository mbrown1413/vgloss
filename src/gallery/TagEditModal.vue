<template>
  <b-modal
    ref="modal"
    title="Edit Tags"
    centered
    ok-title="Save"
    size="xl"
    @ok="onSave"
  >

    <div class="container">
      <div class="row">
        <div class="col-3">

          <Tree
            ref="tree"
            :items="treeData"
            v-model="selectedIds"
          />
          <br>
          <button
            class="btn btn-success"
            @click="addTag"
          >+</button>

        </div>
        <div class="col-9" v-if="selectedTag">

          <h5>{{ selectedTagPath.map(tag => tag.text).join(" &rarr; ") }}</h5>
          <div class="input-group mt-3">
            <div class="input-group-prepend">
              <label class="input-group-text" for="tagEditor-tag-name">
                Name
              </label>
            </div>
            <input v-model="selectedTag.name" class="form-control" id="tagEditor-tag-name">
          </div>

          <div class="input-group mt-3">
            <div class="input-group-prepend">
              <label class="input-group-text" for="tagEditor-tag-parent">
                Parent
              </label>
            </div>
            <select v-model="selectedTag.parent" class="form-control" id="tagEditor-tag-parent">
              <option :value="null">(Root tag)</option>
              <option
                v-for="{tag, depth, disabled} in parentOptions"
                :key="tag.id"
                :value="tag.id"
                :disabled="disabled"
                v-html="'&nbsp;'.repeat(depth*5) + tag.text"
              >
              </option>
            </select>
          </div>

          <button
            class="btn btn-danger mt-5"
            @click="deleteTag(selectedTag.id)"
          >Remove</button>

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
import Tree from '../Tree.vue';

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
      var tagList = JSON.parse(JSON.stringify(this.$store.state.tags));
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

    onSave() {
      this.$store.dispatch("saveTags", Object.values(this.tags));
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
