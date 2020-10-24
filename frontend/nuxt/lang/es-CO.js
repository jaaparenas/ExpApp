export default (context) => {
  return new Promise(function (resolve) {
    resolve({
      'app': {
        'titulo_app': 'Expan APP - Generic',
        'desarrollado_por': 'Desarrollado por ExpansiónTI SAS'
      },
      'comun': {
        'general': {
          'id': 'ID',
          'procesando': 'Procesando',
          'cancelar': 'Cancelar',
          'confirmar': 'Confirmar',
          'cerrar': 'Cerrar',
          'si': 'Si',
          'no': 'No',
          'buscar': 'Buscar',
          'activo': 'Activo',
          'opciones': 'Opciones'
        },
        'administrar': {
          'configuracion': 'Configuración',
          'usuarios': 'Usuarios',
          'grupos': 'Grupos'
        }
      },
      'usuario': {
        'comun': {
          'perfil': 'Perfil'
        },
        'autenticacion': {
          'usuario': 'Nombre de usuario',
          'usuario_contrasegna': 'Debe ingresar su nombre de usuario y/o contraseña',
          'usuario_contrasegna_incorrecto': 'Su nombre de usuario y/o contraseña son incorrectos',
          'correo': 'Correo electrónico',
          'contrasegna': 'Contraseña',
          'olvido_contrasegna': '¿Olvidó su contraseña?',
          'acceder': 'Acceder',
          'cerrar': 'Cerrar sesión',
          'confirmar_cerrar': '¿Realmente desea cerrar su sesión actual?'
        },
        'perfil': {
          'nombres': 'Nombres',
          'apellidos': 'Apellidos',
          'admin': 'Administrador'
        }
      },
      'datos': {
        'comun': {
          'analitica': 'Analítica',
          'subir': 'Subir datos'
        }
      }
    })
  })
}
