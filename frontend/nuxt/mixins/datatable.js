const datatableMixin = {
  data () {
    return {
      draw: 1,
      loading: true,
      items: {},
      options: {
        search: '',
        page: 1,
        itemsPerPage: 5,
        recordsFiltered: 5
      },
      footerProps: {
        'items-per-page-text': this.$t('comunes.herramientas.datatable.itemPorPage')
      }
    }
  },
  watch: {
    options: async function (newData, oldData) {
      this.getData()
    }
  },
  methods: {
    async getData () {
      let self = this
      self.loading = true
      let parameters = {}
      parameters.format = 'datatables'
      parameters.draw = self.draw++
      parameters.keep = 'id'
      self.headers.forEach((colum, index) => {
        if (!self.isset(colum['iscolum'])) {
          parameters['columns[' + index + '][data]'] = colum['value']
          parameters['columns[' + index + '][name]'] = ''
          parameters['columns[' + index + '][searchable]'] = (typeof (colum['filterable']) !== 'undefined' ? colum['filterable'] : 'true')
          parameters['columns[' + index + '][orderable]'] = (typeof (colum['sortable']) !== 'undefined' ? colum['sortable'] : 'true')
          parameters['columns[' + index + '][search][value]'] = ''
          parameters['columns[' + index + '][search][regex]'] = false
        }
      })
      self.headers.forEach((colum, index) => {
        if (self.isset(self.options.sortBy)) {
          if (self.options.sortBy[0] === colum['value']) {
            parameters['order[0][column]'] = index
          }
        }
      })
      if (self.isset(self.options.sortDesc)) {
        parameters['order[0][dir]'] = (self.options.sortDesc[0] === true ? 'desc' : 'asc')
      }
      parameters['start'] = (self.options.page - 1) * self.options.itemsPerPage
      parameters['length'] = self.options.itemsPerPage
      if (self.options.search !== '') { parameters['search[value]'] = self.options.search; parameters['search[regex]'] = false }
      self.items = await self.$axios.$post(self.endpoint, { params: parameters },  { headers: {'Content-Type': 'application/json' }})
      self.loading = false
    }
  }
}
export default datatableMixin
