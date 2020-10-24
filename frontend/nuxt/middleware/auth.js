export default function ({ store, redirect }) {
  if (store.getters.isAuthenticated === false) {
    return redirect('/')
  }
}
