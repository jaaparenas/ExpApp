<template>
  <header class="app-header">
    <NuxtLink to="/escritorio" class="brand">
      <img src="/logo.png" alt="" width="36" height="36">
      <span>ExpAPP</span>
    </NuxtLink>

    <nav v-if="user" class="nav" aria-label="Principal">
      <NuxtLink to="/escritorio">{{ t('nav.dashboard') }}</NuxtLink>
      <NuxtLink to="/datos/subir">{{ t('nav.upload') }}</NuxtLink>
      <NuxtLink to="/datos/analizar">{{ t('nav.analytics') }}</NuxtLink>
      <NuxtLink v-if="user.is_admin" to="/comun/usuario/usuarios">
        {{ t('nav.users') }}
      </NuxtLink>
      <NuxtLink to="/comun/usuario/grupos">{{ t('nav.groups') }}</NuxtLink>
      <NuxtLink to="/comun/usuario/perfil">{{ t('nav.profile') }}</NuxtLink>
    </nav>

    <div v-if="user" class="header-actions">
      <label class="locale">
        <span class="sr-only">{{ t('nav.language') }}</span>
        <select :value="locale" @change="changeLocale">
          <option value="es">ES</option>
          <option value="en">EN</option>
        </select>
      </label>
      <button type="button" class="btn btn--ghost" @click="signOut">
        {{ t('nav.logout') }}
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
const { user, logout } = useAuth()
const { t, locale, setLocale } = useI18n()
const { notify } = useToast()

const changeLocale = (event: Event) => {
  setLocale((event.target as HTMLSelectElement).value as 'es' | 'en')
}

const signOut = async () => {
  await logout()
  notify(t('auth.loggedOut'))
}
</script>
