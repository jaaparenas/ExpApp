import config from '../nuxt.config'
import expLoading from '@/components/expLoading'

const basicMixin = {
  components: { expLoading },
  data () {
    return {
      isLoading: true,
      expApp: config.expapp,
      backendBase: config.expapp.backend_base
    }
  },
  mounted () {
    this.isLoading = false
  },
  methods: {
    isset (obj) {
      return (obj !== null && obj !== undefined && obj !== '')
    },
    create_UUID () {
      var dt = new Date().getTime()
      var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (dt + Math.random() * 16) % 16 | 0
        dt = Math.floor(dt / 16)
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
      })
      return uuid
    },
    fixPageName (name) {
      return name + '___' + this.localeNow
    },
    fixPageRoute (route) {
      let fixRoute = '/' + ((this.$i18n.defaultLocale !== this.localeNow) ? this.localeNow + '/' : '') + route
      fixRoute = fixRoute.replace('//', '/')
      return fixRoute
    },
    openRoute (route) {
      this.$router.push(this.fixPageRoute(route))
    }
  },
  computed: {
    localeNow () {
      return this.$i18n.locale
    },
    getJWT () {
      return (this.isset(this.$auth.getToken('local'))) ? this.$auth.getToken('local').replace('Bearer ', '') : ''
    }
  },
  directives: { }
}
export default basicMixin
