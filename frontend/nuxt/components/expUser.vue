<template>
  <v-card-actions>
    <v-btn color="blue" class="ma-2" dark @click="menu = false; openRoute('/comun/usuario/perfil')">
      <v-icon right>mdi-account-edit</v-icon>&nbsp;{{ $t('usuario.comun.perfil') }}&nbsp;&nbsp;
    </v-btn>
    <v-dialog v-model="salirDialog" persistent max-width="350">
      <template v-slot:activator="{ on }">
        <v-btn color="red" dark v-on="on">
          <v-icon right>mdi-exit-to-app</v-icon>&nbsp;{{ $t('usuario.autenticacion.cerrar') }}&nbsp;&nbsp;
        </v-btn>
      </template>
      <v-card>
        <v-card-title class="headline">{{ $t('usuario.autenticacion.cerrar') }}</v-card-title>
        <v-card-text>{{ $t('usuario.autenticacion.confirmar_cerrar') }}</v-card-text>
        <v-card-actions>
          <v-btn color="green" dark @click="salirDialog=false">
            <v-icon right>mdi-check-circle-outline</v-icon>
            {{ $t('comun.general.no') }}&nbsp;&nbsp;&nbsp;
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="red" dark @click="salirDialog=false; salir()">
            <v-icon right>mdi-exit-to-app</v-icon>
            {{ $t('comun.general.si') }}&nbsp;&nbsp;&nbsp;
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card-actions>
</template>

<script>
  import basicMixins from '@/mixins/basic'

  export default {
    mixins: [ basicMixins ],
    data () {
      return {
        salirDialog: false
      }
    },
    methods: {
      async salir () {
        let self = this
        await this.$axios.$post('/1.0/user/logout', {
          'refresh': self.$auth.getRefreshToken('local')
        }).finally(function (response) {
          self.$auth.logout()
        })
      }
    }
  }
</script>