<template>
  <div class="gallery">
      <GalleryGrid
        :items="items"
        :selectedItems="selectedItems"
        v-model="selectedItems"
      />
    <div
      v-if="selectedItems"
      class="gallery-detail-pane"
    >
      <div v-for="item in selectedItems" :key="item">
        {{ item }}
      </div>
    </div>
  </div>
</template>

<style>
  .gallery {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: 1fr min-content;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
  .gallery-detail-pane {
    background-color: #cccccc;
    border-top: black 2px solid;
    padding-top: 1em;
    padding-bottom: 1em;
  }
</style>

<script>
import GalleryGrid from '../GalleryGrid.vue';

export default {
  name: 'Gallery',
  components: {
    "GalleryGrid": GalleryGrid,
  },
  data() {
    return {
      selectedItems: [],
      items: [
        {name: "Blah 1", image: "http://placekitten.com/300/300"},
        {name: "Blah 2", image: "http://placekitten.com/200/500"},
        {name: "Blah 3eothu neohu nteohuntheontu heonuhoentu h", image: "http://placekitten.com/100/100"},
        {name: "Blah 4", image: "http://placekitten.com/400/300"},
        {name: "Blah 5", image: "http://placekitten.com/200/300"},
        {name: "Blah 6", image: "http://placekitten.com/800/300"},
        {name: "Blah 7", image: "http://placekitten.com/200/300"},
        {name: "Blah theonu heointhonti 8", image: "http://placekitten.com/200/300"},
        {name: "Blah 9", image: "http://placekitten.com/200/300"},
        {name: "Blah 10", image: "http://placekitten.com/300/300"},
        {name: "Blah 11", image: "http://placekitten.com/200/500"},
        {name: "Blah 12eothu neohu nteohuntheontu heonuhoentu h", image: "http://placekitten.com/100/100"},
        {name: "Blah 13", image: "http://placekitten.com/400/300"},
        {name: "Blah 14", image: "http://placekitten.com/200/300"},
        {name: "Blah 15", image: "http://placekitten.com/800/300"},
        {name: "Blah 16", image: "http://placekitten.com/200/300"},
        {name: "Blah theonu heointhonti 17", image: "http://placekitten.com/200/300"},
        {name: "Blah 18", image: "http://placekitten.com/200/300"},
      ],
    };
  },
}
</script>
