<template>
    <Tree
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

export default {
  name: 'FolderFilterTree',
  components: {
    Tree,
  },
  props: {
    tree: {required: true, type: Object},
    selected: {required: false, type: Array, default: () => []},
  },
  data() {
    return {
      opened: [],
    };
  },
  model: {
    prop: "selected",
    event: "change",
  },

  computed: {
    treeComponentData() {
      return [this.buildTreeComponentData("root", this.tree)];
    },
  },

  methods: {

    open(path, toggle=false) {
      var index = this.opened.indexOf(path);
      if(index == -1) {
        this.opened.push(path);
      } else if(toggle) {
        this.opened.splice(index, 1);
      }
    },

    onToggle(event) {
      this.open(event.data.value.path, true);
    },

    onChange(event) {
      this.$emit("change", [event.data.value.path]);
      this.open(event.data.value.path);
    },

    buildTreeComponentData(name, tree, path="", depth=0) {
      var children = [];
      for(var subTreeName in tree) {
        children.push(
          this.buildTreeComponentData(
            subTreeName,
            tree[subTreeName],
            path.length ? path + "/" + subTreeName : subTreeName,
            depth+1,
          )
        );
      }

      return {
        text: name,
        value: {  // Extra user data
          path: path,
        },
        state: {
          opened: this.opened.includes(path),
          selected: this.selected.includes(path),
        },
        children: children,
      };
    },

  },
  watch: {

    selected: {
      handler() {
        for(var path of this.selected) {

          // Open this path
          this.open(path);

          // Open every path leading up to this one
          var parts = path.split("/");
          for(var i=0; i<parts.length; i++) {
            this.open(parts.slice(0, i).join("/"));
          }

        }
      },
      immediate: true,
    },

  },
}
</script>
