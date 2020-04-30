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
        {{ selectedItems.join(" | ") }}
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
      items: [],
    };
  },
  created() {
    // Make API request for items
    var request = new XMLHttpRequest();
    request.addEventListener("load", this.onApiResponse);
    request.open("GET", "/api/gallery/query");
    request.setRequestHeader("Accept", "application/json");
    request.send();
  },
  methods: {
    onApiResponse(event) {
      var xhr = event.target;
      if(xhr.status == 200) {
        this.items = JSON.parse(xhr.response);
      } else {
        //TODO: Error Handling
      }
    },
  },
}
</script>
