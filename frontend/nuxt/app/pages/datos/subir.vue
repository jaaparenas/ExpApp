<template>
  <section>
    <h1>{{ t('upload.title') }}</h1>
    <p class="muted">{{ t('upload.hint') }}</p>

    <form class="card" @submit.prevent="submit">
      <label class="field">
        <span>{{ t('upload.accepted') }}</span>
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.csv,.xls,.xlsx"
          @change="onFileChange"
        >
      </label>

      <p v-if="selectedFile" class="muted">
        {{ selectedFile.name }} · {{ Math.ceil(selectedFile.size / 1024) }} KB
      </p>

      <button
        type="submit"
        class="btn btn--primary"
        :disabled="!selectedFile || loading"
      >
        {{ loading ? t('common.loading') : t('upload.submit') }}
      </button>

      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <p v-if="success" class="success" role="status">{{ success }}</p>
    </form>

    <div v-if="results.length" class="card">
      <h2>{{ t('upload.accepted') }}</h2>
      <ul class="results">
        <li v-for="result in results" :key="result.file">
          <span>{{ result.file }}</span>
          <strong :class="result.disk === 'error' ? 'error' : 'success'">
            {{ result.disk === 'error' ? t('upload.error') : result.disk }}
          </strong>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
const { api } = useAuth()
const { t } = useI18n()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const results = ref<{ file: string, disk: string }[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
  error.value = ''
  success.value = ''
}

const submit = async () => {
  if (!selectedFile.value) {
    return
  }
  error.value = ''
  success.value = ''
  loading.value = true

  const body = new FormData()
  body.append('file', selectedFile.value)

  try {
    const response = await api<{ file: { file: string, disk: string }[] }>(
      '/1.0/datos/subir',
      { method: 'POST', body }
    )
    results.value = response.file || []
    if (results.value.every(item => item.disk !== 'error')) {
      success.value = t('upload.success')
    } else {
      error.value = t('upload.error')
    }
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch {
    error.value = t('upload.error')
  } finally {
    loading.value = false
  }
}
</script>
