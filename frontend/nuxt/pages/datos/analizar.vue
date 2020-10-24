<template>
  <v-row>
    <h1>{{ $t('datos.comun.analitica') }}</h1>
    <v-col cols="12">

    </v-col>
  </v-row>
</template>

<script>
  import basicMixin from '@/mixins/basic'
  import menuMixin from '@/mixins/menu'

  export default {
    mixins: [ basicMixin, menuMixin ],
    components: {

    }
  }
</script>
