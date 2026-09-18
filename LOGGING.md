# Activar logs — iOS

Agregue `debugLogsEnabled` al crear la configuración, antes de iniciar la SDK:

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

Para desactivarlos, use `debugLogsEnabled: false` u omita el argumento. No necesita editar `Info.plist` ni usar el antiguo `logEnabled`.

En Xcode o Console, incluya mensajes **Debug** y filtre por `BecomeSDK`.
## Uso

El valor predeterminado es `false`, también en Release/PROD. Active los logs solo para una prueba y vuelva a desactivarlos al terminar. No cambian el flujo, los tiempos de espera ni los resultados.

## Qué permiten revisar

Muestran el paso del proceso, el estado HTTP, los tiempos y la categoría del error, incluidos captura, prueba de vida, `newIdentity`, consulta de resultados y cierre.

No imprimen credenciales, datos personales, imágenes ni respuestas JSON completas. El parámetro solo controla los logs de Become, no los de la app, el sistema operativo, Microblink o Amplify.

Para soporte, comparta las líneas `BecomeSDK` de la prueba junto con la versión de la SDK y los pasos para reproducir el problema.
