export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuth()

  if (to.path === '/' || to.path === '/reset-password') {
    if (to.path === '/' && auth.loggedIn.value) {
      return navigateTo('/escritorio')
    }
    return
  }

  if (!auth.loggedIn.value) {
    return navigateTo('/')
  }

  if (!auth.user.value) {
    try {
      await auth.fetchUser()
    } catch {
      auth.clear()
      return navigateTo('/')
    }
  }
})
