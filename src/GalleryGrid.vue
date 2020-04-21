<template>
  <div class="gallery-grid">
    <div class="gallery-items">
      <div
        v-for="item in items"
        :key="item.name"
        class="gallery-item-container"
      >
        <div
          class="gallery-item"
        >
          <div
            class="gallery-item-icon"
            :style="{backgroundImage: 'url('+item.thumbnail+')'}"
          />
          {{ item.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<style>
  .gallery-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    grid-gap: 1rem;
    align-items: center;
    padding: 0.5em;
    user-select: none;
  }
  .gallery-item {
    border: 1px solid #d0d0d0;
    border-radius: 5%;
    cursor: pointer;
  }
  .gallery-item:hover {
    border: 1px solid #000000;
  }
  .gallery-item-icon {
    border-radius: 5% 5% 0 0;
    background-position: center center;
    background-size: contain;
    background-repeat: no-repeat;
    /* Padding trick to fix aspect ratio:
     * https://stackoverflow.com/questions/1495407/maintain-the-aspect-ratio-of-a-div-with-css
     */
    width: 100%;
    padding-bottom: 100%;
  }
</style>

<script>
export default {
  name: 'GalleryGrid',
  data() {
    return {
      items: [
        {name: "Blah 1", thumbnail: "http://placekitten.com/g/300/300"},
        {name: "Blah 2", thumbnail: "http://placekitten.com/g/200/500"},
        {name: "Blah 3eothu neohu nteohuntheontu heonuhoentu h", thumbnail: "http://placekitten.com/g/100/100"},
        {name: "Blah 4", thumbnail: "http://placekitten.com/g/400/300"},
        {name: "Blah 5", thumbnail: "http://placekitten.com/g/200/300"},
        {name: "Blah 6", thumbnail: "http://placekitten.com/g/800/300"},
        {name: "Blah 7", thumbnail: "http://placekitten.com/g/200/300"},
        {name: "Blah theonu heointhonti 8", thumbnail: "http://placekitten.com/g/200/300"},
        {name: "Blah 9", thumbnail: "http://placekitten.com/g/200/300"},
      ],
    };
  },
}
</script>
