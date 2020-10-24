const menuMixin = {
  mounted () {
    let MenuTitle = [{ name: this.$t('sipo.menu'), icon: 'fa-puzzle-piece', color: 'bg-success' }]
    let MenuItems = [
      {
        name: this.$t('datos.comun.analitica'),
        icon: 'mdi-database',
        color: 'green',
        visible: true,
        items: [
          {
            name: this.$t('datos.comun.subir'),
            icon: 'mdi-cloud-upload',
            link: '/datos/subir',
            visible: true
          },
          {
            name: 'Analitica',
            icon: 'mdi-chart-bar',
            link: '/datos/analizar',
            visible: true
          }
        ]
      }, {
        name: this.$t('comun.administrar.configuracion'),
        icon: 'mdi-cog',
        color: 'blue',
        visible: true,
        items: [
          {
            name: this.$t('comun.administrar.usuarios'),
            icon: 'mdi-account',
            link: '/comun/usuario/usuarios',
            visible: true
          },
          {
            name: this.$t('comun.administrar.grupos'),
            icon: 'mdi-account-group',
            link: '/comun/usuario/grupos',
            visible: true
          }
        ]
      }
    ]
    this.$store.commit('setMenuTitle', MenuTitle)
    this.$store.commit('setMenuItems', MenuItems)
    this.$store.commit('setMenuShow', true)
  }
}
export default menuMixin