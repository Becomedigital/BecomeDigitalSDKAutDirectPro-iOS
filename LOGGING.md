# Logs de diagnóstico — iOS

## Disponibilidad del binario

**Revisión del 17 de septiembre de 2026:** el XCFramework actualmente incluido en este repositorio todavía no expone `BDIVConfig.debugLogsEnabled` en sus interfaces Swift. Tiene el ajuste heredado `logEnabled = NO`.

La API descrita a continuación ya está implementada en el repositorio fuente `iOS_become_sdk`, pero requiere reemplazar el XCFramework de esta distribución por un build que la incluya y recompilar la aplicación. Esta actualización es solo documental: no sustituye el binario.

Compruebe en Xcode o en los archivos `BDIdentityVerification.swiftinterface` que el inicializador de `BDIVConfig` contiene `debugLogsEnabled`. Si aparece **Extra argument 'debugLogsEnabled' in call**, sigue integrando un framework anterior.

## Activar y desactivar

El parámetro público es **`debugLogsEnabled`**, no `logEnabled`. Es un `Bool` opcional en el inicializador, con valor predeterminado **`false`**, tanto en Debug como en Release/PROD.

Ejemplo para una SDK compatible:

```swift
import BDIdentityVerification

let config = BDIVConfig(
    clienId: clientId,
    clientSecret: clientSecret,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId,
    debugLogsEnabled: true // Activar solo durante el diagnóstico
)

// Conserve esta referencia durante el proceso y registre su BDIVDelegate.
identityVerification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
identityVerification?.startVerification()
```

Para desactivarlo, omita el argumento o use `debugLogsEnabled: false` al crear la configuración. El valor se lee al ejecutar `startVerification()`, no al construir `BecomeDigitalSDK`. El parámetro es inmutable: prepare la configuración antes del inicio.

No necesita cambiar el scheme o usar un framework Debug para habilitarlo en una distribución Release compatible. Para la integración final, déjelo en `false`.

## Ver los logs

Conecte el dispositivo y capture mensajes con Xcode o Console de macOS, incluyendo nivel **Debug**. Filtre por el texto `BecomeSDK`; en Console también puede filtrar por:

- Subsistema: `com.becomedigital.sdk`.
- Categoría: `diagnostics`.
- Proceso: el de su aplicación integradora.

Se utiliza el logging nativo de Apple. No dependa de que los mensajes Debug permanezcan disponibles después del incidente: capture durante la reproducción. [Apple: visualización de mensajes](https://developer.apple.com/documentation/os/viewing-log-messages) y [niveles y almacenamiento](https://developer.apple.com/documentation/os/generating-log-messages-from-your-code).

Ejemplo ilustrativo, con identificador ficticio:

```text
BecomeSDK schema=1 platform=ios run=ce08c779-294a-420e-bf15-d6a33e04d722 seq=12 elapsed_ms=13400 stage=new_identity event=request_failed error=timeout request=3 duration_ms=120001
```

## Qué registra

Los diagnósticos son eventos estructurados de una sola línea. Permiten seguir configuración, permisos, contrato, flujo Onboarding/Authentication, captura documental, prueba de vida, servicios, `newIdentity`, polling y finalización.

| Campo | Significado |
| --- | --- |
| `schema`, `platform` | Versión del formato y plataforma. |
| `run` | UUID aleatorio por ejecución; no es el usuario ni la sesión facial. |
| `seq`, `elapsed_ms` | Orden y tiempo transcurrido desde el inicio. |
| `stage`, `event`, `error` | Etapa, evento y categoría de error predefinidos. |
| `request`, `http_status`, `duration_ms` | Correlación local, estado HTTP y duración de una petición, cuando corresponda. |
| `attempt` | Número de consulta de resultados, cuando corresponda. |

El flag no modifica endpoints, timeouts, polling, navegación ni respuestas entregadas a la aplicación. No habilita verificaciones simultáneas: mantenga una ejecución activa por proceso.

### Cómo interpretar newIdentity y los reintentos

Filtre por `stage=new_identity` y agrupe las líneas por `run`; vincule los eventos HTTP mediante `request`.

| Evento | Interpretación |
| --- | --- |
| `request_started` | Inició la petición. Si no hay evento final, revise cancelación, cierre del proceso o límite de logs. |
| `response_received http_status=...` | Llegó una respuesta HTTP. Un HTTP 200 no garantiza éxito funcional. |
| `request_failed error=timeout` | Timeout de transporte; no significa que la prueba de vida haya sido rechazada. |
| `parse_failed` | No se pudo interpretar la respuesta esperada; el cuerpo no se imprime. |
| `document_rejected` / `document_retry` | Error documental identificado y ruta de recaptura. |
| `liveness_rejected` | Rechazo facial identificado; el flujo debe terminar y devolver el error. |
| `retry_post` / `retry_results` | Ruta de envío de identidad sin URL previa o consulta de resultados con URL previa. También puede marcar la primera entrada en esa ruta. |
| `direct_result` | Se entrega el resultado de `newIdentity` sin polling. |
| `stage=results event=attempt` / `limit_reached` | Consulta de resultados o límite configurado de intentos alcanzado. |
| `stage=completion` | Resultado global: `succeeded`, `failed` o `cancelled`. |

No todos los eventos aparecerán en cada flujo. Los logs ayudan a ubicar una falla, pero no sustituyen el callback ni confirman por sí solos la causa raíz del backend.

## Privacidad y alcance

El nuevo logger de Become excluye desde origen credenciales, tokens, identificadores de usuario/contrato/sesión, nombres, documentos, imágenes, videos, base64, scores biométricos, rutas, URLs reales, query strings, encabezados y cuerpos JSON. Tampoco imprime mensajes ni stack traces de excepciones, mensajes dinámicos del servidor ni objetos completos de respuesta.

Activar el flag **no imprime la respuesta completa de `newIdentity`**: registra metadatos y categorías. Los callbacks conservan su contrato; si la app imprime su contenido, esos logs son responsabilidad del integrador.

El flag solo controla los diagnósticos de Become. No silencia ni habilita los logs de la app, del sistema operativo, Microblink o Amplify. En particular, un mensaje de Android `MI-SF / surfaceflinger` o de iOS `WebContent` no se controla con esta opción.

La SDK no crea archivos de log ni sube estos eventos a un servicio de telemetría. La captura y retención dependen de las herramientas nativas. Al finalizar se deshabilita el diagnóstico de esa ejecución y se ignoran respuestas HTTP tardías de ejecuciones anteriores.

Después de 1.000 eventos ordinarios por ejecución se emite `log_limit` y se omiten los siguientes, conservando el evento de finalización. Esto no detiene las peticiones ni modifica los intentos de polling.

## Qué compartir con soporte

1. Active el flag temporalmente y reproduzca con datos de prueba.
2. Comparta solo las líneas `BecomeSDK` del `run` afectado, junto con la versión/build del SDK, plataforma, versión del sistema, modelo del dispositivo y pasos de reproducción.
3. Revise el archivo exportado: puede contener mensajes de la app o terceros si el filtro no estaba aplicado. No adjunte credenciales, imágenes, datos personales ni respuestas completas.
4. Desactive el flag después de la prueba y limite el acceso y la retención de los registros.

Estas garantías describen la implementación nueva de diagnósticos estructurados, no los loggers heredados ni los registros externos.

## Migración desde logEnabled

En la implementación nueva, agregar `logEnabled` al `Info.plist` de la app o cambiar el valor del framework no habilita el diagnóstico. El control soportado es `BDIVConfig.debugLogsEnabled`; no edite ni vuelva a firmar el framework distribuido para cambiar una bandera.

Los métodos heredados `Logger.shared.log(...)` descartan mensajes libres, incluso con el flag activo. `Logger.shared.configureLogging(isEnabled:)` está obsoleto y solo puede desactivar, no activar logs al margen de `BDIVConfig`.

Si no aparecen eventos, verifique primero el binario compatible, el valor del parámetro antes del inicio, el proceso seleccionado y la inclusión de mensajes Debug. Consulte el [README de integración](README.md) para iniciar y conservar la instancia de la SDK.
