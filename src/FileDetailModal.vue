<template>
  <b-modal
    ref="modal"
    :title="file ? file.name : ''"
    centered
    ok-only
  >
    <div v-if="!details">
      Loading...
    </div>
    <div v-else>
      {{ details }}
    </div>
  </b-modal>
</template>

<script>
import { BModal } from 'bootstrap-vue/esm/components/modal/modal';

export default {
  name: "FileDetailModal",
  components: {
    BModal,
  },
  data() {
    return {
      file: null,
      details: null,
    };
  },
  methods: {

    show(file) {
      this.$refs.modal.show();
      if(!this.file || this.file.hash != file.hash || !this.details) {
        this.file = file;
        this.details = null;  // Set by xhr handler

        // Make API request
        var request = new XMLHttpRequest();
        request.addEventListener("load", this.onDetailApiResponse);
        request.open("GET", "/api/file/"+file.hash);
        request.setRequestHeader("Accept", "application/json");
        request.send();
      }
    },

    onDetailApiResponse(event) {
      var xhr = event.target;
      if(xhr.status == 200) {
        var data = JSON.parse(xhr.response);
        this.details = data;
      } else {
        //TODO: Error Handling
      }
    },

  },
}
</script>
