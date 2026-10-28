# Diagnóstico para soporte en iOS

Activa `debugLogsEnabled` cuando necesites recopilar información para revisar una incidencia de integración. Su valor predeterminado es `false`.

```swift
let config = BDIVConfig(
    clienId: clientId,
    clientSecret: clientSecret,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId,
    debugLogsEnabled: true
)
```

Inicia la SDK con esa configuración como se indica en la [guía de integración](README.md#iniciar-una-verificación). En la consola de Xcode o en Console, incluye los mensajes de nivel **Debug** y filtra por `BecomeSDK`.

Para soporte, indica la versión de la SDK, el dispositivo, la versión de iOS y el paso donde ocurrió el problema. Comparte solo los mensajes relevantes y revisa su contenido antes de enviarlos. No incluyas credenciales, licencias, imágenes ni datos personales.

Al terminar, crea la siguiente configuración con `debugLogsEnabled: false` o sin indicar el parámetro.
