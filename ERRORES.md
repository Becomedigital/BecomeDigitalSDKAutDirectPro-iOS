# Resultados, errores y cancelación en iOS

Implementa `BDIVDelegate` y atiende tanto el resultado como el error antes de iniciar una verificación. Conserva la instancia de la SDK mientras el flujo esté activo.

## Qué recibe tu aplicación

| Notificación | Cómo atenderla |
| --- | --- |
| `BDIVResponseSuccess(bdivResult:)` con `.SUCCES` | Consulta el objeto opcional correspondiente al flujo. En autenticación, evalúa también `authentication.result`. |
| Estado `PENDING` o `NOFOUND` | El resultado no representa una aprobación. |
| `BDIVResponseError(error:)` | Recupera la interfaz de tu aplicación y ofrece un nuevo intento si corresponde. La cancelación del usuario también utiliza este método. |

`onboarding`, `verification` y `authentication` pueden ser `nil`. Los estados y los campos disponibles se describen en la [guía de integración](README.md#consultar-el-resultado).

Si elegiste `performVerificationCheck: false`, `onboarding` confirma la creación del registro, no su aprobación final. Cuando esperas la confirmación, consulta `verification`. Para autenticación, la decisión está en el booleano `authentication.result`.

## Reintentos durante la captura

La SDK presenta las opciones de revisión y reintento disponibles para el usuario. Tu aplicación recibe la notificación al terminar o cancelar el flujo; no recibe una notificación por cada intento de captura.

## Resolver problemas de integración

| Situación | Qué revisar |
| --- | --- |
| No inicia la verificación | JWT vigente sin el prefijo `Bearer` e identificador de contrato no vacío. En autenticación, un `userId` existente. Para la firma deprecada, revisa las credenciales. |
| El token es rechazado | Obtén otro JWT desde el backend de tu aplicación y crea una nueva configuración para reintentar. |
| Creación correcta y HTTP 403 al consultar | Comprueba los permisos por operación: `jwt` para creación y `verificationResultsJwt` para consulta. No basta con cambiar el token principal a `verification:get`. Revisa también vigencia, ambiente y contrato; consulta la [guía de autenticación](AUTENTICACION.md#si-se-crea-la-verificación-pero-la-consulta-devuelve-http-403). |
| No se abre la cámara | Dispositivo físico, descripción `NSCameraUsageDescription` y permiso de cámara concedido. |
| No se habilita la captura de documento | Archivo `com.become.document.key.txt`, pertenencia al destino y coincidencia del identificador de aplicación con la licencia. |
| Xcode indica que falta un módulo | Versiones de paquetes, Xcode y configuración **Embed & Sign** indicados en [Instalación](INSTALACION.md#instalación). |
| La conexión se interrumpe | Recuperar la conectividad y permitir que el usuario vuelva a intentarlo. |
| Se agota la espera del resultado | Revisar `pollingTimeout` y `pollingMaxAttempts` según el comportamiento que necesita tu aplicación. |
| Se solicita repetir el documento o el rostro | Seguir las indicaciones de la pantalla y permitir una nueva captura. |

## Información para soporte

Comparte la versión de la SDK, el modelo del dispositivo, la versión de iOS, el paso visible y una descripción del problema. Si habilitaste el [diagnóstico](LOGGING.md), agrega únicamente las líneas relevantes, después de revisar que no contengan datos personales ni credenciales.

No utilices el texto de `message` o `error` para decidir una aprobación o iniciar reintentos automáticos. Son mensajes descriptivos y pueden variar según el idioma.
