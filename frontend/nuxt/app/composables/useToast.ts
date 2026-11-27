export type ToastType = 'info' | 'success' | 'error'

export interface ToastMessage {
  id: number
  message: string
  type: ToastType
}

export const useToast = () => {
  const toasts = useState<ToastMessage[]>('toasts', () => [])

  const dismiss = (id: number) => {
    toasts.value = toasts.value.filter(toast => toast.id !== id)
  }

  const notify = (message: string, type: ToastType = 'info') => {
    const id = Date.now() + Math.random()
    toasts.value.push({ id, message, type })
    if (import.meta.client) {
      setTimeout(() => dismiss(id), 4500)
    }
  }

  return { toasts, notify, dismiss }
}
