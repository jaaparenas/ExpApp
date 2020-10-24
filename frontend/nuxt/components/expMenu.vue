<template>
  <v-navigation-drawer expand-on-hover app dark class="main_menu">
    <v-list dense class="avatar-list">
      <v-list-item class="px-0" >
        <v-list-item-avatar size="40" class="main_avatar">
          <nuxt-link :to="localePath('/comun/usuario/perfil')">
            <v-img max-width="30" :src="(usuarioDatos.picture != null ? staticBase + '/media/' + usuarioDatos.picture : '/nouser.png')" :alt="nombreCompleto"></v-img>
          </nuxt-link>
        </v-list-item-avatar>
      </v-list-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">
            <span class="user_first_leter">{{ primeraLetra }}</span>
            <span class="user_full_name">{{ nombreCompleto }} </span><br>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <base-menu :items="menuItems" />
  </v-navigation-drawer>
</template>

<script>
import baseMenu from '@/components/baseMenu'
import basicMixin from '@/mixins/basic'

export default {
  name: 'exp-menu',
  mixins: [ basicMixin ],
  components: { baseMenu },
  data: () => ({
    hover: true
  }),
  computed: {
    menuTitle () {
      return this.$store.getters.getMenuTitle
    },
    menuItems () {
      return this.$store.getters.getMenuItems
    },
    usuarioDatos: function () {
      let usuario = this.$store.getters.loggedInUser
      return usuario != null ? usuario : {}
    },
    nombreCompleto () {
      let _userData = this.usuarioDatos
      let _nombreCompleto = ''
      if (this.isset(_userData.first_name) && _userData.first_name.length > 0) {
        _nombreCompleto += _userData.first_name.trim()
      }
      _nombreCompleto += ' '
      if (this.isset(_userData.last_name) && _userData.last_name.length > 0) {
        _nombreCompleto += _userData.last_name.trim()
      }
      return _nombreCompleto
    },
    primeraLetra () {
      return (this.nombreCompleto.length > 0) ? this.nombreCompleto.substr(0, 1) : ''
    }
  }
}
</script>

<style scoped>
.title {
  height: 20px;
}
.v-navigation-drawer--mini-variant .user_first_leter {
  display: show !important;
}
.v-navigation-drawer--mini-variant .user_full_name {
  display: none !important;
}
.v-navigation-drawer--is-mouseover .user_first_leter {
  display: none !important;
}
.v-navigation-drawer--is-mouseover .user_full_name {
  display: show !important;
  text-align: center;
  display: block;
  width: 100%;
}
.main_avatar {
  border: 1px solid #FFF;
}
.main_avatar:first-child {
  margin: auto;
  margin-top: 10px;
}
</style>
