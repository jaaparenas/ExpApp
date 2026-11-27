<template>
  <main class="auth-shell">
    <section class="card auth-card">
      <h1>{{ error?.statusCode === 404 ? '404' : 'Error' }}</h1>
      <p class="muted">{{ message }}</p>
      <NuxtLink class="btn btn--primary" to="/">Volver al inicio</NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
const props = defineProps<{ error: any }>()

const message = computed(() =>
  props.error?.statusCode === 404
    ? 'La página que buscas no existe.'
    : 'Ha ocurrido un error inesperado.'
)
</script>
