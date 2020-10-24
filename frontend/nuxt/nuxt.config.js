const _BASE_BACKEND = 'http://localhost:5000'
const _BASE_BACKEND_API = _BASE_BACKEND + ''
import colors from 'vuetify/es5/util/colors'

export default {
  expapp: {
    backend_base: _BASE_BACKEND
  },
  head: {
    titleTemplate: '%s - ExpAPP',
    title: 'ExpAPP',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },
  css: [
    '@/static/scss/basic.scss'
  ],
  plugins: [
  ],
  components: true,
  buildModules: [
    '@nuxt/typescript-build',
    '@nuxtjs/vuetify'
  ],
  modules: [
    [ '@nuxtjs/auth' ],
    [ '@nuxtjs/axios' ],
    [ '@nuxtjs/proxy' ],
    [ '@nuxtjs/toast' ],
    [ 'nuxt-i18n', {
      locales: [
        { code: 'es-CO', name: 'Español', file: 'es-CO.js', icon: 'colombia.svg' },
        { code: 'en-UK', name: 'English', file: 'en-US.js', icon: 'united-states-of-america.svg' }
      ],
      defaultLocale: 'es-CO',
      lazy: true,
      langDir: 'lang/'
    }]
  ],
  axios: {
    baseURL: _BASE_BACKEND_API,
    proxyHeaders: false,
    credentials: false,
    AllowControlAllowOrigin: '*'
  },
  router: {
    middleware: ['auth']
  },
  auth: {
    localStorage: false,
    strategies: {
      local: {
        endpoints: {
          login: {
            url: '/1.0/user/login',
            method: 'post',
            propertyName: 'access'
          },
          refresh: {
            url: '/1.0/user/refresh',
            method: 'post',
            propertyName: 'refresh'
          },
          logout: false,
          user: { url: '/1.0/user/data', method: 'get', propertyName: false }
        },
        tokenRequired: true,
        tokenType: 'Bearer'
      }
    },
    redirect: {
      login: '/',
      logout: '/',
      user: '/comun/usuario/perfil',
      home: '/escritorio'
    }
  },
  vuetify: {
    customVariables: ['~/assets/variables.scss'],
    theme: {
      dark: true,
      themes: {
        dark: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.accent3
        }
      }
    }
  },
  build: {
  }
}
