<template>
  <v-row>
    <h1>{{ $t('usuario.comun.perfil') }}</h1>
    <v-col cols="12">
      <v-row>
        <v-col cols="6">
          <exp-search :searchFunction="searchFunction" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="headers"
            :items="items.data"
            :items-per-page="5"
            :server-items-length="items.recordsFiltered"
            :options.sync="options">
            <template v-slot:item.opciones="{ item }">
              <v-menu offset-y>
                <template v-slot:activator="{ on }">
                  <v-btn color="blue" small dark v-on="on">{{ $t('comun.general.opciones') }}</v-btn>
                </template>
                <v-list>
                  <v-list-item>
                    <v-list-item-title>Editar</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table>
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
    name: 'page-comun-usuarios',
    mixins: [ basicMixin, menuMixin, datatableMixin ],
    components: { expSearch },
    data () {
      return {
        endpoint: '/1.0/user/users',
        headers: [
          { text: this.$t('comun.general.id'), value: '0', width: 50, sortable: false, filterable: false },
          { text: this.$t('usuario.autenticacion.usuario'), value: '1', sortable: true, filterable: true },
          { text: this.$t('usuario.perfil.nombres'), value: '2', sortable: true, filterable: true },
          { text: this.$t('usuario.perfil.apellidos'), value: '3', sortable: true, filterable: true },
          { text: this.$t('usuario.autenticacion.correo'), value: '4', sortable: false, filterable: false },
          { text: this.$t('comun.general.activo'), value: '5', width: 80, sortable: false, filterable: false },
          { text: this.$t('usuario.perfil.admin'), value: '6', width: 80, sortable: false, filterable: false },
          { text: this.$t('comun.general.opciones'), value: 'opciones', width: 80, sortable: false, filterable: false },
        ]
      }
    },
    mounted () {
      this.getData()
    },
    methods: {
      async searchFunction (text) {
        this.options.search = text
        this.options.page = 1
        this.getData()
      }
    }
  }
</script>
