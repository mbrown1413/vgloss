<template>
  <GalleryGrid
    :items="items"
  />
</template>

<script>
import GalleryGrid from '../GalleryGrid.vue';

export default {
  name: 'Gallery',
  components: {
    "GalleryGrid": GalleryGrid,
  },
  data() {
    return {
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
