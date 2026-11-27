<template>
  <section class="auth-shell">
    <form class="card auth-card" @submit.prevent="submit">
      <div class="auth-brand">
        <img src="/logo.png" alt="" width="56" height="56">
        <h1>ExpAPP</h1>
      </div>
      <p class="muted">{{ t('auth.subtitle') }}</p>

      <label class="field">
        <span>{{ t('auth.username') }}</span>
        <input v-model="username" autocomplete="username" required autofocus>
      </label>

      <label class="field">
        <span>{{ t('auth.password') }}</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        >
      </label>

      <button type="submit" class="btn btn--primary" :disabled="loading">
        {{ loading ? t('auth.loggingIn') : t('auth.login') }}
      </button>

      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <div class="auth-footer">
        <NuxtLink to="/reset-password">{{ t('auth.forgot') }}</NuxtLink>
        <select :value="locale" aria-label="Idioma" @change="changeLocale">
          <option value="es">ES</option>
          <option value="en">EN</option>
        </select>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'blank' })

const { login, loggedIn } = useAuth()
const { t, locale, setLocale } = useI18n()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

onMounted(() => {
  if (loggedIn.value) {
    navigateTo('/escritorio')
  }
})

const changeLocale = (event: Event) => {
  setLocale((event.target as HTMLSelectElement).value as 'es' | 'en')
}

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await login(username.value.trim(), password.value)
    await navigateTo('/escritorio')
  } catch {
    error.value = t('auth.error')
  } finally {
    loading.value = false
  }
}
</script>
