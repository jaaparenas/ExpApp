<template>
  <section>
    <h1>{{ t('profile.title') }}</h1>

    <div class="grid grid--two">
      <article class="card">
        <dl class="details">
          <dt>{{ t('profile.username') }}</dt>
          <dd>{{ user?.username }}</dd>
          <dt>{{ t('profile.email') }}</dt>
          <dd>{{ user?.email }}</dd>
          <dt>{{ t('profile.firstName') }}</dt>
          <dd>{{ user?.first_name || '—' }}</dd>
          <dt>{{ t('profile.lastName') }}</dt>
          <dd>{{ user?.last_name || '—' }}</dd>
          <dt>{{ t('profile.admin') }}</dt>
          <dd>{{ user?.is_admin ? t('common.yes') : t('common.no') }}</dd>
        </dl>
      </article>

      <form class="card" @submit.prevent="changePassword">
        <h2>{{ t('profile.changePassword') }}</h2>

        <label class="field">
          <span>{{ t('profile.currentPassword') }}</span>
          <input
            v-model="currentPassword"
            type="password"
            autocomplete="current-password"
            required
          >
        </label>

        <label class="field">
          <span>{{ t('profile.newPassword') }}</span>
          <input
            v-model="newPassword"
            type="password"
            autocomplete="new-password"
            minlength="8"
            required
          >
        </label>

        <label class="field">
          <span>{{ t('profile.confirm') }}</span>
          <input
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            minlength="8"
            required
          >
        </label>

        <button type="submit" class="btn btn--primary" :disabled="loading">
          {{ loading ? t('common.loading') : t('common.save') }}
        </button>

        <p v-if="error" class="error" role="alert">{{ error }}</p>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
const { user, api, clear } = useAuth()
const { t } = useI18n()
const { notify } = useToast()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

const changePassword = async () => {
  error.value = ''
  loading.value = true
  try {
    await api('/1.0/user/change_password', {
      method: 'POST',
      body: {
        current_password: currentPassword.value,
        password: newPassword.value,
        confirm: confirmPassword.value
      }
    })
    notify(t('profile.updated'), 'success')
    clear()
    await navigateTo('/')
  } catch (requestError: any) {
    const msg = requestError?.data?.msg
    if (msg === '_BAD_PASSWORD') {
      error.value = t('profile.badPassword')
    } else if (msg === '_PASSWORD_MISMATCH') {
      error.value = t('profile.mismatch')
    } else if (msg === '_WEAK_PASSWORD') {
      error.value = t('reset.weak')
    } else {
      error.value = t('auth.error')
    }
  } finally {
    loading.value = false
  }
}
</script>
