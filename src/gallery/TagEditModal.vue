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
        <div class="col-9" v-if="selectedTag">

          <h5>{{ tagPath(selectedTag).map(tag => tag.name).join(" &rarr; ") }}</h5>
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
                v-for="[tag, depth] in parentOptions"
                :key="tag.id"
                :value="tag.id"
                :disabled="tagDescendantIds(selectedId).includes(tag.id)"
                v-html="'&nbsp;'.repeat(depth*5) + tag.name"
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
import {Tree} from "tree-vue-component";

/* TagEditModal
 * Edit tree of tags.
 *
 * There are a few different datatypes used here internally and externally to
 * track information about tags:
 *
 *   * Tag ID - Idetnifier used everywhere to uniquely reference a tag. Integer
 *       tag IDs are saved to the database, while string tag IDs are temporary,
 *       and are replaced with integers when the tag is saved.
 *   * Tag Object - The tag structure presented and stored in the backend API.
 *   * Tag tree and nodes - Generated in the computed property
 *       `treeComponentData`, this is a derived data structure storing
 *       information for the tree component. This is also used as a convenience
 *       in other methods because it stores a list of children and a reference
 *       to the tag object for each node.
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
      selectedId: null,
      opened: [],
    };
  },
  created() {
    this.tempCounter = 0;

    // nodesById is generated inside `treeComponentData`. It isn't good
    // practice for computed properties to have side effects, but it's
    // convenient in this case.
    this.nodesById = {};  // Map tag ID to tree node
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
        };
      }
      // Add child nodes to their parent
      for(tag of Object.values(this.tags)) {
        if(tag.parent !== null) {
          nodesById[tag.parent].children.push(
            nodesById[tag.id]
          )
        }
      }
      // Sort childern alphabetically
      for(var node of Object.values(nodesById)) {
        node.children.sort((a, b) => {
          a = a.text.toUpperCase();
          b = b.text.toUpperCase();
          if (a < b) {
            return -1;
          } else if(a > b) {
            return 1;
          } else {
            return 0;
          }
        });
      }
      // Open path leading up to selected node
      if(this.selectedId !== null) {
        for(tag of this.tagPath(this.tags[this.selectedId])) {
          // Open in local nodesById and also add to this.opened for future
          // updates.
          nodesById[tag.id].state.opened = true;
          this.openTag(tag.id);
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

    /* Dropdown options for the selected tag's parent. */
    parentOptions() {
      var options = [];
      var stack = [];

      for(var node of this.treeComponentData) {
        stack.unshift({node: node, depth: 0});
      }

      while(stack.length) {
        var stackItem = stack.pop();
        node = stackItem.node;
        var depth = stackItem.depth;

        options.push([node.value, depth]);
        for(var child of node.children) {
          stack.push({node: child, depth: depth+1});
        }
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

      this.selectedId = null;
      this.$refs.modal.show();
    },

    openTag(tagId, toggle=false) {
      var index = this.opened.indexOf(tagId);
      if(index == -1) {
        this.opened.push(tagId);
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
        parent: null,
      });
      this.selectedId = newId;
    },

    deleteTag(tagId) {
      this.$delete(this.tags, tagId);
      if(this.selectedId == tagId) {
        this.selectedId = null;
      }

      function findNode(nodes, id) {
        for(var node of nodes) {
          if(node.value.id == id) {
            return node;
          }
          var foundNode = findNode(node.children, id);
          if(foundNode != null) {
            return foundNode;
          }
        }
        return null;
      }
      var tagNode = findNode(this.treeComponentData, tagId);

      // Delete all children too
      for(var child of tagNode.children) {
        this.deleteTag(child.value.id);
      }
    },

    tagPath(tag) {
      var path = [];
      do {
        path.unshift(tag);
        tag = tag.parent !== null ? this.tags[tag.parent] : null;
      } while(tag);
      return path;
    },

    /* List of the IDs of the given tag's childen, their children, etc.
     * Includes the given tag ID for convenience. */
    tagDescendantIds(id) {
      // Two-pass approach to getting all descendants.
      // 1) Build list of children for each tag
      var childrenByTagId = {};  // Map tag ID to list of children.
      for(var tag of Object.values(this.tags)) {
        var childId = tag.id;
        var parentId = tag.parent;
        if(childId !== null) {
          if(childrenByTagId[parentId] === undefined) {
            childrenByTagId[parentId] = [];
          }
          childrenByTagId[parentId].push(childId);
        }
      }
      // 2) Start list with given Id and expand to children until an
      //    iteration adds no more descendants.
      var descendants = [id];
      var frontier = [id];  // New IDs this round
      do {
        var newFrontier = [];
        for(id of frontier) {
          if(childrenByTagId[id] !== undefined) {
            newFrontier.push(...childrenByTagId[id]);
          }
        }
        frontier = newFrontier;
        descendants.push(...frontier);
      } while(frontier.length > 0);
      return descendants;
    },

  },
}
</script>
