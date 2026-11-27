const messages: Record<string, Record<string, any>> = {
  es: {
    auth: {
      subtitle: 'Accede con tu cuenta',
      username: 'Usuario',
      password: 'Contraseña',
      login: 'Acceder',
      loggingIn: 'Accediendo…',
      forgot: '¿Olvidaste tu contraseña?',
      error: 'Usuario o contraseña incorrectos',
      invalidSession: 'La sesión expiró. Vuelve a iniciar sesión.',
      loggedOut: 'Sesión cerrada.'
    },
    nav: {
      dashboard: 'Escritorio',
      upload: 'Subir datos',
      analytics: 'Analítica',
      users: 'Usuarios',
      groups: 'Grupos',
      profile: 'Perfil',
      logout: 'Salir',
      language: 'Idioma'
    },
    common: {
      loading: 'Cargando…',
      search: 'Buscar',
      actions: 'Acciones',
      cancel: 'Cancelar',
      save: 'Guardar',
      active: 'Activo',
      yes: 'Sí',
      no: 'No'
    },
    dashboard: {
      title: 'Escritorio',
      welcome: 'Bienvenido',
      uploadHint: 'Sube archivos CSV o Excel para analizarlos.',
      profileHint: 'Consulta tus datos y cambia tu contraseña.'
    },
    profile: {
      title: 'Perfil',
      username: 'Usuario',
      email: 'Correo',
      firstName: 'Nombres',
      lastName: 'Apellidos',
      admin: 'Administrador',
      changePassword: 'Cambiar contraseña',
      currentPassword: 'Contraseña actual',
      newPassword: 'Nueva contraseña',
      confirm: 'Confirmar contraseña',
      updated: 'Contraseña actualizada. Inicia sesión de nuevo.',
      sessionsClosed: 'Se cerraron las sesiones activas.',
      badPassword: 'La contraseña actual no es correcta.',
      mismatch: 'Las contraseñas no coinciden.'
    },
    users: {
      title: 'Usuarios',
      hint: 'Administra las cuentas registradas.',
      forbidden: 'No tienes permisos para ver esta sección.',
      error: 'No se pudieron cargar los usuarios.',
      id: 'ID',
      firstName: 'Nombres',
      lastName: 'Apellidos',
      active: 'Activo',
      admin: 'Admin',
      empty: 'No hay usuarios para mostrar.'
    },
    upload: {
      title: 'Subir datos',
      hint: 'Formatos permitidos: .txt, .csv, .xls y .xlsx (máximo 8 MB).',
      accepted: 'Archivos aceptados',
      submit: 'Subir archivo',
      success: 'Archivo subido correctamente',
      error: 'No se pudo subir el archivo'
    },
    analytics: {
      title: 'Analítica',
      hint: 'Aquí se mostrarán los análisis de los datos cargados.'
    },
    groups: {
      title: 'Grupos',
      hint: 'La administración de grupos estará disponible próximamente.'
    },
    reset: {
      title: 'Recuperar contraseña',
      hint: 'Define una nueva contraseña para tu cuenta.',
      newPassword: 'Nueva contraseña',
      confirm: 'Confirmar contraseña',
      submit: 'Actualizar contraseña',
      success: 'Contraseña actualizada. Ya puedes iniciar sesión.',
      invalid: 'El enlace no es válido o ya expiró.',
      weak: 'La contraseña debe tener al menos 8 caracteres.',
      mismatch: 'Las contraseñas no coinciden.',
      back: 'Volver al inicio de sesión'
    }
  },
  en: {
    auth: {
      subtitle: 'Sign in to your account',
      username: 'Username',
      password: 'Password',
      login: 'Sign in',
      loggingIn: 'Signing in…',
      forgot: 'Forgot your password?',
      error: 'Invalid username or password',
      invalidSession: 'Session expired. Please sign in again.',
      loggedOut: 'Signed out.'
    },
    nav: {
      dashboard: 'Dashboard',
      upload: 'Upload data',
      analytics: 'Analytics',
      users: 'Users',
      groups: 'Groups',
      profile: 'Profile',
      logout: 'Sign out',
      language: 'Language'
    },
    common: {
      loading: 'Loading…',
      search: 'Search',
      actions: 'Actions',
      cancel: 'Cancel',
      save: 'Save',
      active: 'Active',
      yes: 'Yes',
      no: 'No'
    },
    dashboard: {
      title: 'Dashboard',
      welcome: 'Welcome',
      uploadHint: 'Upload CSV or Excel files to analyze them.',
      profileHint: 'Review your data and change your password.'
    },
    profile: {
      title: 'Profile',
      username: 'Username',
      email: 'Email',
      firstName: 'First name',
      lastName: 'Last name',
      admin: 'Administrator',
      changePassword: 'Change password',
      currentPassword: 'Current password',
      newPassword: 'New password',
      confirm: 'Confirm password',
      updated: 'Password updated. Please sign in again.',
      sessionsClosed: 'Active sessions were closed.',
      badPassword: 'The current password is incorrect.',
      mismatch: 'Passwords do not match.'
    },
    users: {
      title: 'Users',
      hint: 'Manage registered accounts.',
      forbidden: 'You do not have permission to view this section.',
      error: 'Users could not be loaded.',
      id: 'ID',
      firstName: 'First name',
      lastName: 'Last name',
      active: 'Active',
      admin: 'Admin',
      empty: 'No users to display.'
    },
    upload: {
      title: 'Upload data',
      hint: 'Allowed formats: .txt, .csv, .xls and .xlsx (max 8 MB).',
      accepted: 'Accepted files',
      submit: 'Upload file',
      success: 'File uploaded successfully',
      error: 'The file could not be uploaded'
    },
    analytics: {
      title: 'Analytics',
      hint: 'Analytics for uploaded data will be shown here.'
    },
    groups: {
      title: 'Groups',
      hint: 'Group management will be available soon.'
    },
    reset: {
      title: 'Reset password',
      hint: 'Choose a new password for your account.',
      newPassword: 'New password',
      confirm: 'Confirm password',
      submit: 'Update password',
      success: 'Password updated. You can sign in now.',
      invalid: 'The link is invalid or has expired.',
      weak: 'The password must be at least 8 characters long.',
      mismatch: 'Passwords do not match.',
      back: 'Back to sign in'
    }
  }
}

export const useI18n = () => {
  const locale = useCookie<'es' | 'en'>('expapp_locale', {
    default: () => 'es',
    sameSite: 'lax'
  })

  const t = (key: string): string => {
    const dictionary = messages[locale.value] || messages.es
    const value = key.split('.').reduce<any>(
      (current, part) => (current ? current[part] : undefined),
      dictionary
    )
    return typeof value === 'string' ? value : key
  }

  const setLocale = (value: 'es' | 'en') => {
    locale.value = value
  }

  return { locale, t, setLocale }
}
