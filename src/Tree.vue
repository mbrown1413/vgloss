<template>
  <VueTree
    :data="treeComponentData"
    @toggle="onToggle"
    @change="onChange"
  />
</template>

<style>
  @import "~tree-component/dist/tree.css";
</style>

<script>
import {Tree} from "tree-vue-component";

/* Tree
 * The tree UI element used throughout Vgloss.
 *
 * Although this uses tree-vue-component to do the heavy lifting, this
 * component ensures that tree behavior such as opening, closing, and
 * selecting nodes is consistent throughout the UI.
 */
export default {
  name: "Tree",
  components: {
    VueTree: Tree,
  },
  model: {
    prop: "selectedIds",
    event: "changeSelected",
  },
  props: {
    // List of items to display in tree. For each item, following
    // properties are recognized:
    //   * id: A unique identifier referenced by "parent".
    //   * text: Text to display in the tree.
    //   * parent: The parent of this item, or null if no parent.
    items: {required: true, type: Array},

    // If true, show checkboxes to allow multiple items to be selected.
    //multiSelect: {required: false, type: Boolean, default: false},

    // Optional: List of selected item IDs
    selectedIds: {required: false, type: Array, default: () => []},
  },
  data() {
    return {
      openedIds: [],
    };
  },
  computed: {

    treeComponentData() {
      // Create flat list of tree nodes indexed by item ID
      var nodesById = {};
      for(var item of this.items) {
        nodesById[item.id] = {
          text: item.text,
          value: item,
          icon: false,  //TODO
          state: {
            opened: this.openedIds.includes(item.id),
            selected: this.selectedIds.includes(item.id),
          },
          children: [],
        };
      }

      // Add child nodes to their parent
      for(item of this.items) {
        if(item.parent !== null && item.parent !== undefined) {
          nodesById[item.parent].children.push(
            nodesById[item.id]
          );
        }
      }

      // Sort children alphanumerically by text
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

      // Return root nodes (ones without parents)
      return Object.values(nodesById).filter((node) =>
        node.value.parent === null || node.value.parent === undefined
      );
    },

    /* Map item ID to list of IDs leading to the item with that ID. */
    pathById() {
      var pathById = {};
      function recurse(nodes, path=[]) {
        for(var node of nodes) {
          pathById[node.value.id] = path;
          var newPath = path.slice();
          newPath.push(node.value.id);
          recurse(node.children, newPath);
        }
      }
      recurse(this.treeComponentData);
      return pathById;
    },

  },
  methods: {

    open(nodeId, toggle=false) {
      var index = this.openedIds.indexOf(nodeId);
      if(index == -1) {
        this.openedIds.push(nodeId);
      } else if(toggle) {
        this.openedIds.splice(index, 1);
      }
    },

    openToggle(nodeId) {
        this.open(nodeId, true);
    },

    /* Event Handlers */

    onChange(event) {
      this.$emit("changeSelected", [event.data.value.id]);
      this.open(event.data.value.path);
    },

    onToggle(event) {
      this.openToggle(event.data.value.id);
    },

  },
  watch: {

    selectedIds: {
      handler() {
        for(var id of this.selectedIds) {
          // Open this node
          this.open(id);

          // Open nodes leading up to this one
          // If id not found in pathById, maybe it hasn't been initialized yet.
          // Ignore it for now, and when pathById updates this watcher will be
          // called again.
          for(var idInPath of this.pathById[id] || []) {
            this.open(idInPath);
          }
        }
      },
      immediate: true,
    },

  },
}
</script>