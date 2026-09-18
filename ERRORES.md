# Manejo de errores — iOS

## Qué recibe la aplicación

| Salida | Cómo se entrega | Qué debe hacer la app |
| --- | --- | --- |
| Éxito | `BDIVResponseSuccess(bdivResult:)`, con `BDIdentityVerificationResponse` | Comprobar `responseStatus == .SUCCES`. |
| Error terminal | `BDIVResponseError(error: String)` | Restaurar su pantalla y ofrecer una acción al usuario; no reiniciar automáticamente la SDK. |
| Cancelación del proceso | El mismo callback de error, con el texto de `cancel_by_user` | Permitir continuar en la app sin considerar la identidad aprobada. No existe `onCancel` en iOS. |
| Error recuperable | Pantalla de reintento o recaptura dentro de la SDK | Dejar que la SDK gestione el flujo; no se emite un callback por cada fallo. |

`SUCCES` conserva esa escritura por compatibilidad. Aunque el modelo define `ERROR`, `PENDING` y `NOFOUND`, el coordinador entrega las salidas no exitosas por el callback **de texto**, no como un objeto de error. `responseDictionary` es opcional y no es un catálogo de errores.

Con `performVerificationCheck: false`, un éxito significa que `newIdentity` aceptó la creación, **no que terminó o aprobó la validación biométrica**. El diccionario puede contener `code`, `message`, `url_resource` y `user_id`.

### Límite del mapeo

Actualmente no se devuelve un `errorCode`, una clave de localización ni un código HTTP separado. Las claves de esta guía identifican textos; **no son valores recibidos en `error`**. El idioma, la personalización y algunos mensajes del servicio cambian el texto. No base decisiones de aprobación, bloqueo o reintento automático en comparaciones del mensaje.

Si necesita distinguir programáticamente cada causa, se requiere ampliar el contrato público de la SDK; no basta con esta documentación. Mantenga una salida segura para mensajes desconocidos o vacíos.

## Errores de inicio y otros flujos

Los siguientes casos pueden finalizar con `BDIVResponseError`. Los nombres de claves conservan las erratas existentes por compatibilidad.

| Clave o mensaje identificable | Cuándo ocurre | Acción recomendada |
| --- | --- | --- |
| `error_clientid_empty` — `ClienId parameters cannot be empty` | `clienId` vacío | Corregir la configuración antes de iniciar. |
| `error_client_secret_empty` — `ClientSecret parameters cannot be empty` | Credencial vacía | Revisar la integración, sin mostrar ni registrar la credencial. |
| `error_contractid_empty` — `ContractId parameters cannot be empty` | Contrato vacío | Configurar el contrato entregado al cliente. |
| `error_userid_emty` — `UserId parameters cannot be empty` | Usuario vacío | Asignar el identificador del proceso. |
| `error_vallidationtype_empty` — `The validationTypes parameter cannot be empty` | `documenTypes` vacío en `.Onboarding` | Habilitar al menos un tipo documental; `.Authentication` admite la lista vacía. |
| `text_msn_error_config` — `Incorrect SDK configuration` / `Configuración de la SDK incorrecta` | El `delegate` no es un `UIViewController` que implemente `BDIVDelegate` | Iniciar desde un controlador compatible. |
| `License file not found` o mensaje de Microblink | Falta la licencia o falla la inicialización documental | Revisar archivo, inclusión en el target y Bundle Identifier autorizado. |
| `liveness_detection_failed`, o prefijo `Liveness detection failed:` en Authentication | Fallo de captura, sesión facial o lectura de su resultado | Ofrecer iniciar una nueva ejecución; no reutilizar la sesión facial. El detalle puede variar. |
| `error_low_confidence` | `/matches` devuelve `result=false` | Tratar la autenticación como fallida; ofrecer una nueva verificación según la política de la app. |
| `timeout_error`, `no_internet_error`, `connection_lost_error` | Fallo de conexión, por ejemplo durante Authentication | Revisar la red y ofrecer reintento iniciado por el usuario. |
| Mensaje del servicio o de una dependencia, sin clave fija | Autenticación inicial, contrato, `/matches` u otro componente | No asumir un catálogo cerrado; mostrar una alternativa segura y contactar con soporte si persiste. |
| `general_error`, `unknown_error` | Inicialización de Amplify, respuesta no interpretable u otro fallo no clasificado | Validar configuración y dependencias; usar diagnóstico para soporte. |
| `text_error_compliance_not_allowed` | Cierre desde una pantalla de validación fallida de versiones anteriores | No considerar la verificación aprobada. |
| `cancel_by_user` — `Cancelado por el usuario` | El usuario confirma la salida; también puede ocurrir al cancelar el flujo facial de Authentication | Restaurar la pantalla de la app. Cancelar solo la captura facial de Onboarding puede regresar a su introducción sin finalizar la SDK. |

Los permisos de cámara y avisos de captura también pueden mostrarse dentro de la SDK o por iOS; no todos generan una salida al cliente.

## Catálogo ampliado de creación y resultados

Este catálogo está incluido en el XCFramework de este repositorio e incorpora el mapeo del repositorio fuente `4118013`. Si utiliza una copia anterior, reemplace el XCFramework completo; agregar textos en la app no actualiza el comportamiento del binario.

Aplica a `POST /api/v1/newIdentity`, con o sin polling, y a GET de resultados cuando está habilitado. No sustituye el manejo independiente de `/matches`, autenticación inicial ni los errores de las dependencias.

- **Cerrar:** se cierra la interfaz de la SDK y se entrega `BDIVResponseError`. La aplicación anfitriona permanece abierta.
- **Recapturar:** la SDK abre el error documental y permite volver a capturar; no entrega todavía un error terminal.
- **Reintentar:** la SDK muestra el mensaje y detiene las consultas hasta la acción del usuario; tampoco entrega un error terminal automáticamente.

| Clave de texto | Causa reconocida / significado del mensaje | Acción de la SDK y manejo recomendado |
| --- | --- | --- |
| `identity_error_liveness` | Prueba de vida no confirmada, incluido `liveness=false` | Cerrar. Iniciar un proceso nuevo si el usuario desea reintentar. |
| `identity_error_face` | Rostro no validado, incluido `face_match=false` | Cerrar. Nueva verificación con el rostro descubierto. |
| `identity_error_documentFront` | Frente ilegible o `documentError=1` | Recapturar el frente completo, enfocado y sin reflejos. |
| `identity_error_documentBack` | Reverso ilegible o `documentError=2` | Recapturar el lado correcto. |
| `identity_error_documentFiles` | Archivos documentales no recibidos correctamente o lados incorrectos | Recapturar los lados solicitados. |
| `identity_error_documentQuality` | Calidad insuficiente o datos documentales no legibles | Recapturar con buena luz y enfoque. |
| `identity_error_documentUnsupported` | Tipo documental no reconocido/admitido | Recapturar con un tipo admitido. |
| `identity_error_documentValidation` | Documento no validado; por ejemplo `alteration=false` o `template=false` | Recapturar. Revisar original, vigencia y tipo; no interpretar el mensaje como prueba de fraude. |
| `identity_error_session` | Sesión vencida/no válida; token o HTTP 401 | Reintentar disponible. Se recomienda cerrar e iniciar una nueva sesión. |
| `identity_error_permission` | Operación no habilitada; HTTP 403 | Reintentar disponible. Revisar permisos con soporte. |
| `identity_error_configuration` | Parámetros requeridos ausentes o inválidos | Reintentar disponible. Corregir la integración antes de iniciar otra ejecución. |
| `identity_error_contract` | No se pudo validar el contrato | Reintentar disponible. Revisar el contrato con soporte. |
| `identity_error_quota` | Saldo/cupo de verificaciones no disponible | Reintentar disponible. Contactar con soporte. |
| `identity_error_notFound` | Usuario/verificación no encontrado; HTTP 404 | Reintentar disponible. Comprobar el proceso con soporte. |
| `identity_error_conflict` | Ya existe un proceso asociado; HTTP 409 | Reintentar disponible. Resolver el conflicto; evitar nuevas altas automáticas. |
| `identity_error_uploadSize` | Archivos demasiado grandes; HTTP 413 | Reintentar disponible. El mensaje recomienda cerrar y hacer una nueva captura. |
| `identity_error_fileFormat` | Formato no compatible; HTTP 415 | Reintentar disponible. Nueva captura o soporte. |
| `identity_error_rateLimit` | Demasiadas solicitudes; HTTP 429 | Reintentar después de esperar. |
| `identity_error_unavailable` | Servicio no disponible; HTTP 5xx salvo 504 u otro fallo de transporte | Reintentar más tarde. |
| `identity_error_processing` | No se completó el procesamiento; HTTP 400/422 sin causa más específica | Reintentar; contactar con soporte si persiste. |
| `identity_error_invalidResponse` | Respuesta vacía, inválida, desconocida o evidencia requerida incompleta | Reintentar; nunca asumir aprobación. |
| `identity_error_timeout` | Tiempo de espera agotado, HTTP 408/504 o límite de intentos de polling alcanzado | Reintentar tras revisar la conexión. El límite no cierra la SDK automáticamente. |
| `identity_error_offline` | Sin conexión a Internet | Reconectar y reintentar. |
| `identity_error_connection` | Conexión interrumpida o fallo de conexión/resolución del servidor | Revisar la red y reintentar. |

Las causas del cuerpo de la respuesta tienen prioridad sobre el mapeo HTTP genérico: **HTTP 400 no significa necesariamente error documental**. Las categorías son internas; no equivalen a códigos públicos del backend ni llegan separadas al callback.

### Cómo se reintenta

Con polling habilitado, sin URL guardada se reenvían los mismos datos a `newIdentity`; con URL guardada se reinicia la consulta GET. Sin polling, el reintento vuelve al POST y nunca inicia GET. Un error documental descarta las capturas documentales y la URL anteriores para recapturar. Un rechazo facial cierra la SDK y exige un proceso nuevo.

Un resultado pendiente no es un error: sigue consultándose. `pollingMaxAttempts=0` no limita intentos; un límite positivo detiene el polling y muestra reintento al agotarse. Si el usuario decide salir desde un error recuperable, recibe la salida de cancelación, no necesariamente la causa del servicio anterior.

## Ejemplo de manejo seguro

Implemente estos métodos en el controlador que actúa como `BDIVDelegate`:

```swift
func BDIVResponseSuccess(bdivResult: AnyObject) {
    guard let response = bdivResult as? BDIdentityVerificationResponse,
          response.responseStatus == .SUCCES else {
        BDIVResponseError(error: "")
        return
    }
    // Si performVerificationCheck es false: creación aceptada, no aprobación final.
    // Continúe según el flujo configurado. responseDictionary puede ser nil.
}

func BDIVResponseError(error: String) {
    DispatchQueue.main.async {
        // Restaure los controles de su app. No relance la SDK automáticamente.
        // El texto puede ser una cancelación o un detalle técnico variable.
        let alert = UIAlertController(
            title: "Verificación no completada",
            message: "El proceso terminó sin completar la verificación. Puedes volver a iniciarlo.",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "Aceptar", style: .default))
        self.present(alert, animated: true)
    }
}
```

El ejemplo usa un texto neutral porque el callback no permite distinguir todas las causas de forma estructurada. Para adaptar mensajes, consulte [Localización](LOCALIZACION.md) y las claves `identity_error_*` de la plantilla. No registre `error`, respuestas completas, imágenes ni credenciales. Para soporte use los [logs de diagnóstico](LOGGING.md), la versión de la SDK y el paso donde falló.
