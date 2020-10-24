<template>
  <v-container>
    <v-navigation-drawer temporary :right="true" v-model="rightDrawer" fixed width="350">
      <exp-chat />
    </v-navigation-drawer>
    <v-footer fixed app>
      <!-- <v-btn x-large :color="colorTema" absolute top right fab @click="rightDrawer=true" class="btn_chat text-white">
        <v-icon x-large>chat</v-icon>
      </v-btn> -->
      <span class="caption">{{ $t('aplicacion.titulo') }} </span>
    </v-footer>
  </v-container>
</template>

<script>
  import expChat from '@/components/layouts/expChat'

  export default {
    name: 'exp_footer',
    components: { expChat },
    data () {
      return {
        rightDrawer: false
      }
    },
    computed: {
      EsModoOscuro () {
        return this.$store.getters.getModoOscuro
      },
      colorTema () {
        return this.$store.getters.getColorTheme
      }
    }
  }
</script>

<style scoped lang="styl">
  /* .btn_chat {
    margin-top: -40px;
    background: rgb(5,219,159);
    background: linear-gradient(0deg, rgba(5,219,159,1) 34%, rgba(1,193,238,1) 95%);
  } */
</style>
