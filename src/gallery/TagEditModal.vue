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
            :data="treeComponentData"
            @change="onChange"
            @toggle="onToggle"
          />
          <br>
          <button
            class="btn btn-success"
            @click="addTag"
          >+</button>

        </div>
        <div class="col-9" v-if="selectedId">

          <h5>{{ tagPath(selectedTag).join(" -> ") }}</h5>
          <div class="input-group">
            <div class="input-group-prepend">
              <label class="input-group-text" for="tagEditor-tag-name">
                Name
                </label>
            </div>
            <input v-model="selectedTag.name" id="tagEditor-tag-name">
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
import {Tree} from "tree-vue-component";

export default {
  name: "TagEditModal",
  components: {
    BModal,
    Tree,
  },
  data() {
    return {
      tags: {},  // Map tag ID to tag object
      selectedId: null,
      opened: [],
    };
  },
  created() {
    this.tempCounter = 0;
  },
  computed: {

    treeComponentData() {
      // Create flat list of tree nodes indexed by id
      var nodesById = {};
      for(var tag of Object.values(this.tags)) {
        nodesById[tag.id] = {
          text: tag.name,
          value: tag,
          icon: false,
          state: {
            opened: this.opened.includes(tag.id),
            selected: this.selectedId == tag.id,
          },
          children: [],
        }
      }
      // Add child nodes to their parent
      for(tag of Object.values(this.tags)) {
        if(tag.parent !== null) {
          nodesById[tag.parent].children.push(
            nodesById[tag.id]
          )
        }
      }
      // Return root nodes (ones without parents)
      return Object.values(nodesById).filter((node) =>
        node.value.parent === null
      );
    },

    selectedTag() {
      return this.tags[this.selectedId] || null;
    },

  },
  methods: {

    show() {
      // Convert tag list to mapping from tag ID
      var tagList = JSON.parse(JSON.stringify(this.$store.state.tags));
      this.tags = {};
      for(var tag of tagList) {
        this.tags[tag.id] = tag;
      }

      this.$refs.modal.show();
    },

    openTag(path, toggle=false) {
      var index = this.opened.indexOf(path);
      if(index == -1) {
        this.opened.push(path);
      } else if(toggle) {
        this.opened.splice(index, 1);
      }
    },

    onToggle(event) {
      this.openTag(event.data.value.id, true);
    },

    onChange(event) {
      this.selectedId = event.data.value.id;
      this.openTag(event.data.value.id);
    },

    onSave() {
      //TODO
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
        parent: null,
      });
      this.selectedId = newId;
    },

    tagPath(tag) {
      var path = [];
      while(tag !== null) {
        path.unshift(tag.name);
        tag = tag.parent;
      }
      return path;
    },

  },
}
</script>
