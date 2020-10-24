<template>
  <v-text-field
    v-model="search"
    append-icon="mdi-magnify"
    :label="$t('comun.general.buscar') + '...'"
    single-line
    hide-details
    clearable
    autocomplete="off">
  </v-text-field>
</template>

<script>
  export default {
    name: 'exp-search',
    data () {
      return {
        search: '',
        searchDelay: Object
      }
    },
    watch: {
      search: async function (newData, oldData) {
        let self = this
        clearTimeout(this.searchDelay)
        this.searchDelay = setTimeout(function () {
          self._search()
        }, 1000)
      }
    },
    props: {
      searchFunction: {
        type: Function,
        default: null
      }
    },
    methods: {
      _search () {
        this.searchFunction((this.search == null) ? '' : this.search)
      }
    }
  }
</script>