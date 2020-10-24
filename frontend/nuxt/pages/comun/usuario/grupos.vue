<template>
  <v-row>
    <h1>{{ $t('comun.administrar.grupos') }}</h1>
    <v-col cols="12">
      <v-row>
        <v-col cols="6">
          <exp-search :searchFunction="searchFunction" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">

        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>


<script>
  import basicMixin from '@/mixins/basic'
  import menuMixin from '@/mixins/menu'
  import datatableMixin from '@/mixins/datatable'
  import expSearch from '@/components/expSearch'

  export default {
    name: 'page-comun-grupos',
    mixins: [ basicMixin, menuMixin, datatableMixin ],
    components: { expSearch },
    methods: {
      async searchFunction (text) {

      }
    }
  }
</script>