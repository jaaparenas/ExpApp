<template>
  <section>
    <h1>{{ t('groups.title') }}</h1>
    <p class="muted">{{ t('groups.hint') }}</p>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n()
</script>
