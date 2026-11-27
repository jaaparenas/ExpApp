<template>
  <section class="auth-shell">
    <form class="card auth-card" @submit.prevent="submit">
      <h1>{{ t('reset.title') }}</h1>

      <template v-if="!done">
        <p class="muted">{{ t('reset.hint') }}</p>

        <label class="field">
          <span>{{ t('reset.newPassword') }}</span>
          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            minlength="8"
            required
            :disabled="!valid"
          >
        </label>

        <label class="field">
          <span>{{ t('reset.confirm') }}</span>
          <input
            v-model="confirm"
            type="password"
            autocomplete="new-password"
            minlength="8"
            required
            :disabled="!valid"
          >
        </label>

        <button type="submit" class="btn btn--primary" :disabled="!valid || loading">
          {{ loading ? t('common.loading') : t('reset.submit') }}
        </button>

        <p v-if="error" class="error" role="alert">{{ error }}</p>
      </template>

      <template v-else>
        <p class="success" role="status">{{ t('reset.success') }}</p>
        <NuxtLink class="btn btn--primary" to="/">{{ t('reset.back') }}</NuxtLink>
      </template>
    </form>
  </section>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'blank' })

const route = useRoute()
const config = useRuntimeConfig()
const { t } = useI18n()

const token = computed(() => String(route.query.token || ''))
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const valid = ref(false)
const done = ref(false)
const error = ref('')

onMounted(async () => {
  if (!token.value) {
    error.value = t('reset.invalid')
    return
  }
  try {
    await $fetch(`/1.0/user/reset_password/${encodeURIComponent(token.value)}`, {
      baseURL: config.public.apiBase
    })
    valid.value = true
  } catch {
    error.value = t('reset.invalid')
  }
})

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await $fetch(`/1.0/user/reset_password/${encodeURIComponent(token.value)}`, {
      baseURL: config.public.apiBase,
      method: 'POST',
      body: { password: password.value, confirm: confirm.value }
    })
    done.value = true
  } catch (requestError: any) {
    const msg = requestError?.data?.msg
    if (msg === '_WEAK_PASSWORD') {
      error.value = t('reset.weak')
    } else if (msg === '_PASSWORD_MISMATCH') {
      error.value = t('reset.mismatch')
    } else {
      error.value = t('reset.invalid')
    }
  } finally {
    loading.value = false
  }
}
</script>
