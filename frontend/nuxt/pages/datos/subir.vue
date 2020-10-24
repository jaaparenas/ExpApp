<template>
  <v-row>
    <h1>{{ $t('datos.comun.subir') }}</h1>
    <v-col cols="12">
      <dropzone id="up_file" ref="up_file" :options="options" :destroyDropzone="true"></dropzone>
    </v-col>
  </v-row>
</template>


<script>
  import basicMixin from '@/mixins/basic'
  import menuMixin from '@/mixins/menu'
  import Dropzone from 'nuxt-dropzone'
  import 'nuxt-dropzone/dropzone.css'

  export default {
    name: 'page-datos-subir',
    mixins: [ basicMixin, menuMixin ],
    components: { Dropzone },
    data() {
      return {
        instanceDZ: Object,
        arrayFiles: [],
        options: {
          url: `${this.$axios.defaults.baseURL}` + '/1.0/datos/subir',
          headers: { 'Authorization': this.$auth.getToken('local') },
          addRemoveLinks: true,
          duplicateCheck: true,
          acceptedFiles: '.txt,.csv,.xls,.xlsx,',
          dictInvalidFileType: this.$t('comunes.archivos.dictInvalidFileType'),
          dictRemoveFile: this.$t('comunes.archivos.dictRemoveFile'),
          uploadMultiple: false

        }
      }
    },
    mounted() {
      let self = this
      this.instanceDZ = this.$refs.up_file.dropzone
      this.instanceDZ.on('success', function (file, response) {
        self.arrayFiles.push({ key: response, value: file })
      })
      this.instanceDZ.on('removedfile', function (file) {
        self.arrayFiles.forEach(function (item, index, object) {
          if (item.value === file) {
            object.splice(index, 1)
          }
        })
      })
    }
  }
</script>

<style scoped>
  #upFile {

  }
</style>