<template>
  <div class="home">
    <b-button @click="openModal">Launch demo modal</b-button>

    <b-modal ref="modal-1" title="BootstrapVue">
      <p class="my-4">Hello from modal!</p>
    </b-modal>

  </div>
</template>

<script>
// @ is an alias to /src
//import HelloWorld from '@/components/HelloWorld.vue'
import { BModal, BButton } from 'bootstrap-vue'

export default {
  name: 'Home',
  components: {
    //HelloWorld,
    BModal,
    BButton,
  },
  methods: {
    openModal() {
      this.$refs['modal-1'].show();
    },
  },
}
</script>
