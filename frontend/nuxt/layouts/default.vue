<template>
  <v-app>
    <exp-menu />
    <v-app-bar dark fixed app>
      <v-toolbar-title dark>
        <router-link :to="{path: '/'}">
          <v-img max-width="200" src="/logo.png" alt="ExpAPP"></v-img>
        </router-link>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <exp-user />
    </v-app-bar>
    <v-main>
      <v-container class="container-fluid p-0 d-flex flex-column container-p">
        <exp-loading v-show="isLoading" />
        <exp-bread-crumb />
        <nuxt />
      </v-container>
    </v-main>
    <v-footer app>
      <span class="white--text">&copy; {{ new Date().getFullYear() }}</span>
    </v-footer>
  </v-app>
</template>

<script>
  import basicMixins from '@/mixins/basic'
  import expLoading from '@/components/expLoading'
  import expUser from '@/components/expUser'
  import expMenu from '@/components/expMenu'
  import expBreadCrumb from '@/components/expBreadCrumb'

  export default {
    mixins: [ basicMixins ],
    components: { expLoading, expUser, expMenu, expBreadCrumb },
    data () {
      return {
        clipped: true,
        drawer: false,
        fixed: false,
        items: [
          {
            icon: 'mdi-apps',
            title: 'Welcome',
            to: '/'
          },
          {
            icon: 'mdi-chart-bubble',
            title: 'Inspire',
            to: '/inspire'
          }
        ],
        miniVariant: false,
        right: true,
        rightDrawer: false,
        title: 'Vuetify.js'
      }
    }
  }
</script>
