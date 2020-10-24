<template>
  <div class="page-login">
    <exp-loading v-show="isLoading" />
    <v-row align="center" justify="center" v-show="!isLoading && !isLoggedIn">
      <v-card class="elevation-20 card-login">
        <v-card-title>
          <h2>{{ $t('usuario.autenticacion.acceder') }}</h2>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="login()">
            <v-text-field :label="$t('usuario.autenticacion.usuario')" v-model="username" type="text" />
            <v-text-field :label="$t('usuario.autenticacion.contrasegna')" v-model="password" type="password" v-on:keyup.enter="login()"/>
          </v-form>
        </v-card-text>
        <v-card-actions style="text-aling:center" class="px-5 pb-0">
          <v-btn @click="login()" dark :disabled="!btn_acceder">
            <v-icon>mdi-lock</v-icon>&nbsp;&nbsp;{{ $t('usuario.autenticacion.acceder') }}
          </v-btn>
        </v-card-actions>
        <v-card-text>
          <v-row>
            <v-col>
              {{ $t('usuario.autenticacion.olvido_contrasegna') }}
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-row>
  </div>
</template>

<script>
  import basicMixins from '@/mixins/basic'

  export default {
    layout: 'blank',
    name: 'login',
    mixins: [ basicMixins ],
    components: { },
    data () {
      return {
        user: {
        },
        username: '',
        password: '',
        btn_acceder: true
      }
    },
    created () {
      if (this.isLoggedIn) {
        this.openRoute(this.urlhome)
      }
    },
    computed: {
      isLoggedIn () {
        return this.$store.getters.getIsLoggedIn
      }
    },
    methods: {
      async login () {
        let self = this
        this.isLoading = true
        this.btn_acceder = false
        if (this.username.length > 0 && this.password.length > 0) {
          await this.$auth.loginWith('local', {
            data: {
              username: self.username,
              password: self.password
            }
          }).then((response) => {
            this.isLoading = false
            this.$auth.setRefreshToken('local', response.data.refresh)
          }).catch((error) => {
            this.isLoading = false
            this.msgError(this.$t('usuario.autenticacion.usuario_contrasegna_incorrecto'))
          })
        } else {
          this.isLoading = false
          this.msgError(this.$t('usuario.autenticacion.usuario_contrasegna'))
        }
      },
      msgError(msg) {
        this.$toast.show(msg, {
          type: 'error',
          theme: 'bubble',
          duration: 1500,
          position: 'bottom-center'
        })
        setTimeout(() => { this.btn_acceder = true }, 1500)
      }
    }
  }
</script>
