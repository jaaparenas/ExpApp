<template>
  <section>
    <h1>{{ t('analytics.title') }}</h1>
    <p class="muted">{{ t('analytics.hint') }}</p>
    <NuxtLink class="btn btn--primary" to="/datos/subir">
      {{ t('nav.upload') }}
    </NuxtLink>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n()
</script>
