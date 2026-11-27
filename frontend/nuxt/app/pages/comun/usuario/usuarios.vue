<template>
  <section>
    <h1>{{ t('users.title') }}</h1>

    <p v-if="forbidden" class="error" role="alert">{{ t('users.forbidden') }}</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>

    <template v-if="!forbidden">
      <div class="toolbar">
        <input
          v-model="search"
          type="search"
          :placeholder="t('common.search')"
          :aria-label="t('common.search')"
        >
      </div>

      <div class="table-wrap card">
        <table>
          <thead>
            <tr>
              <th v-for="header in headers" :key="header.key">
                {{ t(header.label) }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="headers.length" class="muted">{{ t('common.loading') }}</td>
            </tr>
            <tr v-else-if="items.length === 0">
              <td :colspan="headers.length" class="muted">{{ t('users.empty') }}</td>
            </tr>
            <template v-else>
              <tr v-for="item in items" :key="item['0']">
                <td>{{ item['0'] }}</td>
                <td>{{ item['1'] }}</td>
                <td>{{ item['2'] || '—' }}</td>
                <td>{{ item['3'] || '—' }}</td>
                <td>{{ item['4'] }}</td>
                <td>{{ item['5'] ? t('common.yes') : t('common.no') }}</td>
                <td>{{ item['6'] ? t('common.yes') : t('common.no') }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button
          type="button"
          class="btn btn--ghost"
          :disabled="page <= 1 || loading"
          @click="goToPage(page - 1)"
        >
          ←
        </button>
        <span>{{ page }} / {{ totalPages }}</span>
        <button
          type="button"
          class="btn btn--ghost"
          :disabled="page >= totalPages || loading"
          @click="goToPage(page + 1)"
        >
          →
        </button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
const { api } = useAuth()
const { t } = useI18n()

const headers = [
  { key: '0', label: 'users.id' },
  { key: '1', label: 'profile.username' },
  { key: '2', label: 'users.firstName' },
  { key: '3', label: 'users.lastName' },
  { key: '4', label: 'profile.email' },
  { key: '5', label: 'users.active' },
  { key: '6', label: 'users.admin' }
]

const items = ref<Record<string, any>[]>([])
const total = ref(0)
const page = ref(1)
const perPage = 10
const search = ref('')
const loading = ref(false)
const forbidden = ref(false)
const error = ref('')
let draw = 1
let searchTimer: ReturnType<typeof setTimeout> | undefined

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)))

const buildParams = () => {
  const params: Record<string, string> = {
    draw: String(draw++),
    start: String((page.value - 1) * perPage),
    length: String(perPage),
    'search[value]': search.value,
    'search[regex]': 'false',
    'order[0][column]': '0',
    'order[0][dir]': 'asc'
  }
  headers.forEach((_, index) => {
    params[`columns[${index}][data]`] = String(index)
    params[`columns[${index}][name]`] = ''
    params[`columns[${index}][searchable]`] = 'true'
    params[`columns[${index}][orderable]`] = 'true'
    params[`columns[${index}][search][value]`] = ''
    params[`columns[${index}][search][regex]`] = 'false'
  })
  return params
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api<{
      data: Record<string, any>[]
      recordsTotal: string
      recordsFiltered: string
    }>('/1.0/user/users', {
      method: 'POST',
      body: { params: buildParams() }
    })
    items.value = response.data || []
    total.value = Number(response.recordsFiltered || response.recordsTotal || 0)
  } catch (requestError: any) {
    if (requestError?.response?.status === 403) {
      forbidden.value = true
    } else {
      error.value = t('users.error')
    }
  } finally {
    loading.value = false
  }
}

const goToPage = (nextPage: number) => {
  page.value = Math.min(Math.max(1, nextPage), totalPages.value)
  load()
}

watch(search, () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
})

onMounted(load)
</script>
