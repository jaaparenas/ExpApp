export interface TokenPair {
  access: string
  refresh: string
}

export interface AuthUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const access = useCookie<string | null>('expapp_access', {
    sameSite: 'lax',
    secure: !import.meta.dev,
    maxAge: 60 * 60 * 24
  })
  const refreshToken = useCookie<string | null>('expapp_refresh', {
    sameSite: 'lax',
    secure: !import.meta.dev,
    maxAge: 60 * 60 * 24 * 7
  })
  const user = useState<AuthUser | null>('auth_user', () => null)
  const loggedIn = computed(() => Boolean(access.value))

  const setTokens = (tokens: TokenPair) => {
    access.value = tokens.access
    refreshToken.value = tokens.refresh
  }

  const clear = () => {
    access.value = null
    refreshToken.value = null
    user.value = null
  }

  const withAuth = (options: Record<string, any> = {}) => {
    const headers = { ...(options.headers || {}) }
    if (access.value) {
      headers.Authorization = `Bearer ${access.value}`
    }
    return { ...options, headers }
  }

  const request = <T>(path: string, options: Record<string, any> = {}) =>
    $fetch<T>(path, {
      baseURL: config.public.apiBase,
      ...withAuth(options)
    })

  const api = async <T>(path: string, options: Record<string, any> = {}): Promise<T> => {
    const { _retry, ...requestOptions } = options
    try {
      return await request<T>(path, requestOptions)
    } catch (error: any) {
      if (error?.response?.status !== 401 || !refreshToken.value || _retry) {
        throw error
      }
      try {
        const tokens = await $fetch<TokenPair>('/1.0/user/refresh', {
          baseURL: config.public.apiBase,
          method: 'POST',
          body: { refresh: refreshToken.value }
        })
        setTokens(tokens)
        return await request<T>(path, { ...requestOptions, _retry: true })
      } catch (refreshError) {
        clear()
        await navigateTo('/')
        throw refreshError
      }
    }
  }

  const fetchUser = async () => {
    user.value = await api<AuthUser>('/1.0/user/data')
    return user.value
  }

  const login = async (username: string, password: string) => {
    const tokens = await $fetch<TokenPair>('/1.0/user/login', {
      baseURL: config.public.apiBase,
      method: 'POST',
      body: { username, password }
    })
    setTokens(tokens)
    try {
      await fetchUser()
    } catch (error) {
      clear()
      throw error
    }
  }

  const logout = async () => {
    try {
      await api('/1.0/user/logout', {
        method: 'POST',
        body: { refresh: refreshToken.value }
      })
    } catch {
      // Si el token ya expiró, igualmente limpiamos la sesión local.
    }
    clear()
    await navigateTo('/')
  }

  return {
    access,
    refreshToken,
    user,
    loggedIn,
    api,
    login,
    logout,
    fetchUser,
    clear,
    setTokens
  }
}
