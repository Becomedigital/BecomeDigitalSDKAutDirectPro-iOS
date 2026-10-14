# Manejo de errores — iOS

## Salidas públicas

| Salida | Manejo recomendado |
| --- | --- |
| `BDIVResponseSuccess(bdivResult:)` con `.SUCCES` | Revise el objeto opcional correspondiente al flujo. En autenticación, evalúe también `authentication.result`. |
| `BDIVResponseError(error:)` | Restaure la pantalla de la app y ofrezca una acción para iniciar de nuevo. También se usa cuando el usuario cancela. |

`SUCCES` mantiene esa escritura por compatibilidad. `error` es un texto descriptivo, no un código estable. Los objetos `onboarding`, `authentication` y `verification` pueden ser `nil`. Si `performVerificationCheck=false`, `onboarding` indica que se inició el proceso; no equivale a un resultado final aprobado.

La SDK muestra dentro de su propia interfaz las opciones de reintento disponibles. La app no recibe un callback por cada intento de captura.

## Problemas que puede resolver la app

- **Configuración incompleta:** compruebe `clienId`, `clientSecret`, `contractId`, `userId` y los tipos documentales requeridos para onboarding.
- **Cámara no disponible o permiso denegado:** compruebe el dispositivo y `NSCameraUsageDescription`.
- **Licencia de captura:** verifique `com.become.document.key.txt` y el Bundle Identifier autorizado.
- **Conexión interrumpida:** permita un nuevo intento iniciado por el usuario cuando vuelva la conectividad.
- **Captura no completada:** deje que el usuario repita la captura desde la SDK.

No use comparaciones de `error` para decidir aprobación o reintentos automáticos: el texto puede cambiar por idioma o personalización. Si el problema persiste, comparta con soporte la versión de la SDK, el paso donde ocurrió y los [logs de diagnóstico](LOGGING.md). No incluya credenciales ni imágenes.
