<template>
  <section>
    <h1>{{ t('dashboard.title') }}</h1>
    <p class="welcome">
      {{ t('dashboard.welcome') }},
      <strong>{{ user?.first_name || user?.username }}</strong>
    </p>

    <div class="grid">
      <NuxtLink class="card link-card" to="/datos/subir">
        <h2>{{ t('nav.upload') }}</h2>
        <p class="muted">{{ t('dashboard.uploadHint') }}</p>
      </NuxtLink>

      <NuxtLink class="card link-card" to="/comun/usuario/perfil">
        <h2>{{ t('nav.profile') }}</h2>
        <p class="muted">{{ t('dashboard.profileHint') }}</p>
      </NuxtLink>

      <NuxtLink
        v-if="user?.is_admin"
        class="card link-card"
        to="/comun/usuario/usuarios"
      >
        <h2>{{ t('nav.users') }}</h2>
        <p class="muted">{{ t('users.hint') }}</p>
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
const { user } = useAuth()
const { t } = useI18n()
</script>
