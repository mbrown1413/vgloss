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
    event: "change-selected",
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

      /* Map item ID to list of IDs leading to the item with that ID. */
      pathById: {},

      /* Map ID to the node with that ID. */
      nodesById: {},
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
          icon: false,
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
          var parent = nodesById[item.parent];
          if(parent === undefined) {
            throw "Item id "+item.id+" references nonexistant parent id "+item.parent;
          }
          parent.children.push(
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
      //TODO: Sort this alphabetically too
      return Object.values(nodesById).filter((node) =>
        node.value.parent === null || node.value.parent === undefined
      );
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

    /* Tree helpers */

    walkTree: function*() {
      var stack = [];
      for(var node of this.treeComponentData) {
        stack.unshift({node: node, depth: 0});
      }
      while(stack.length) {
        var stackItem = stack.pop();
        yield {
          id: stackItem.node.value.id,
          item: stackItem.node.value,
          depth: stackItem.depth,
        };
        for(var child of stackItem.node.children) {
          stack.push({node: child, depth: stackItem.depth+1});
        }
      }
    },

    /* List of the IDs of the given item's childen, their children, etc. */
    getDescendantItems: function*(itemId) {
      // Start list with given Id and expand to children until an iteration
      // adds no more descendants.
      var node = this.nodesById[itemId];
      if(node === undefined) {
        return;
      }
      var frontier = [node];  // New nodes this iteration
      do {
        var newFrontier = [];
        for(node of frontier) {
          newFrontier.push(...node.children);
          yield node.value;
        }
        frontier = newFrontier;
      } while(frontier.length > 0);
    },

    /* List of items leading to the given ID starting at the root */
    getItemPath: function*(itemId) {
      var path = this.pathById[itemId];
      if(path === undefined) {
        return [];
      }
      for(var id of path) {
        yield this.nodesById[id].value;
      }
    },

    /* Event Handlers */

    onChange(event) {
      this.$emit("change-selected", [event.data.value.id]);
      this.open(event.data.value.path);
    },

    onToggle(event) {
      this.openToggle(event.data.value.id);
    },

  },
  watch: {

    treeComponentData: {
      handler() {
        this.pathById = {};
        this.nodesById = {};

        var recurse = (nodes, path=[]) => {
          for(var node of nodes) {
            this.pathById[node.value.id] = path.concat(node.value.id);
            this.nodesById[node.value.id] = node;

            var newPath = path.slice();
            newPath.push(node.value.id);
            recurse(node.children, newPath);
          }
        };
        recurse(this.treeComponentData);
      },
      immediate: true,
    },

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
