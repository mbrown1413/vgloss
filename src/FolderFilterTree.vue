<template>
    <Tree
      :data="treeData"
      @toggle="toggle"
    />
</template>

<style>
@import "~tree-component/dist/tree.css";
</style>

<script>
import {Tree} from "tree-vue-component";

const rawData = [
  {
    text: 'node 1',
    state: {opened: false},
    children: [
      {
        text: 'loading node 2',
        state: {},
        children: [],
      },
      {
        text: 'loading node 2',
        state: {},
        children: [],
      },
      {
        text: 'loading node 2',
        state: {},
        children: [],
      }
    ],
  },
  {
    text: 'loading node 2',
    state: {},
    children: [],
  }
];

export default {
  name: 'FolderFilterTree',
  components: {
    Tree,
  },
  props: {},
  data() {
    return {
      treeData: rawData,
    };
  },
  methods: {
    toggle(event) {
      event.data.state.opened = !event.data.state.opened;
    },
  },
}
</script>
