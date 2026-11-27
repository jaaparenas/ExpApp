<template>
  <div class="toasts" aria-live="polite" aria-atomic="true">
    <button
      v-for="toast in toasts"
      :key="toast.id"
      type="button"
      :class="['toast', `toast--${toast.type}`]"
      @click="dismiss(toast.id)"
    >
      {{ toast.message }}
    </button>
  </div>
</template>

<script setup lang="ts">
const { toasts, dismiss } = useToast()
</script>
