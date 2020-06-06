<template>
  <b-modal
    ref="modal"
    :title="file ? file.name : ''"
    centered
    ok-only
    ok-title="Close"
    size="xl"
    v-model="visible"
  >
    <div v-if="!details">
      Loading...
    </div>
    <div v-else>
      <img :src="imageUrl" />
      {{ details }}
    </div>
  </b-modal>
</template>

<script>
import { BModal } from "bootstrap-vue/esm/components/modal/modal";
import * as urls from "./urls.js";

import LRU from "lru-cache";

var detailCache = new LRU(20);

export default {
  name: "FileDetailModal",
  components: {
    BModal,
  },
  data() {
    return {
      file: null,
      details: null,
      visible: false,
    };
  },
  mounted() {
    document.addEventListener("keydown", (event) => {
      if(this.visible) {
        if(["ArrowUp", "ArrowLeft"].includes(event.code)) {
          this.$emit("prev");
        } else if(["ArrowDown", "ArrowRight"].includes(event.code)) {
          this.$emit("next");
        }
      }
    });
  },
  computed: {
    imageUrl() {
      return urls.fileRaw(this.file.hash);
    },
  },
  methods: {

    show(file) {
      this.$refs.modal.show();
      if(!this.file || this.file.hash != file.hash || !this.details) {
        this.file = file;
        this.details = null;  // Set by xhr handler

        var details = detailCache.get(file.hash);
        if(details !== undefined) {
          this.details = details;
        } else {
          // Make API request
          var xhr = new XMLHttpRequest();

          var onResponse = () => {
            if(xhr.status == 200) {
              var data = JSON.parse(xhr.response);
              // If the request is slow, the current file may have changed.
              // Always update the cache, but only update details if the files
              // match.
              detailCache.set(file.hash, data);
              if(file.hash == this.file.hash) {
                this.details = data;
              }
            } else {
              //TODO: Error Handling
            }
          }

          xhr.addEventListener("load", onResponse);
          xhr.open("GET", urls.apiFileDetail(file.hash));
          xhr.setRequestHeader("Accept", "application/json");
          xhr.send();
        }
      }
    },

  },
}
</script>
