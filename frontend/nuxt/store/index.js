export const state = () => ({
  menu_title: [],
  menu_items: [],
  menu_show: false,
  breadcrumb_items: [],
  breadcrumb_show: false
})

export const mutations = {
  setMenuTitle (state, menuTitle) {
    state.menu_title = menuTitle
  },
  setMenuItems (state, menuItems) {
    state.menu_items = menuItems
  },
  setMenuShow (state, menuShow) {
    state.menu_show = menuShow
  },
  setBreadcrumbItems (state, breadcrumbItems) {
    state.breadcrumb_items = breadcrumbItems
  },
  setBreadcrumbShow (state, breadcrumbShow) {
    state.breadcrumb_show = breadcrumbShow
  }
}

export const getters = {
  isAuthenticated(state) {
    return state.auth.loggedIn
  },
  loggedInUser(state) {
    return state.auth.user
  },
  getMenuItems (state) {
    return state.menu_items
  },
  getMenuTitle (state) {
    return state.menu_title
  },
  getMenuShow (state) {
    return state.menu_show
  },
  getBreadcrumbItems (state) {
    return state.breadcrumb_items
  },
  getBreadcrumbShow (state) {
    return state.breadcrumb_show
  }
}