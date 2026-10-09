# Diagnóstico — iOS

Para una prueba, active el parámetro al crear la configuración:

```swift
let config = BDIVConfig(
    clienId: clientId,
    clientSecret: clientSecret,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId,
    debugLogsEnabled: true
)
identityVerification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
identityVerification?.startVerification()
```

El valor predeterminado es `false`; vuelva a desactivarlo al terminar. En Xcode o Console, incluya mensajes **Debug** y filtre por `BecomeSDK`.

Para solicitar soporte, indique la versión de la SDK, el dispositivo, el paso visible y las líneas relevantes de `BecomeSDK`. Revise cualquier registro antes de compartirlo para excluir información personal.
