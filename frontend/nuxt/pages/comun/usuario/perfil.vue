<template>
  <v-row>
    <h1>{{ $t('usuario.comun.perfil') }}</h1>
    <v-col cols="12">
    </v-col>
  </v-row>
</template>


<script>
  import basicMixin from '@/mixins/basic'
  import menuMixin from '@/mixins/menu'
  import datatableMixin from '@/mixins/datatable'
  import expSearch from '@/components/expSearch'

  export default {
    name: 'page-comun-perfil',
    mixins: [ basicMixin, menuMixin, datatableMixin ],
    components: { expSearch }
  }
</script>