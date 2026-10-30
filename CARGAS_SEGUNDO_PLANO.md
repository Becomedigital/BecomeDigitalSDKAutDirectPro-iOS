# Continuidad en segundo plano en iOS

Si tu aplicación admite continuar la transferencia de la verificación al pasar a segundo plano, reenvía el evento correspondiente a la SDK desde `AppDelegate`:

```swift
import UIKit
import BDIdentityVerification

func application(_ application: UIApplication,
                 handleEventsForBackgroundURLSession identifier: String,
                 completionHandler: @escaping () -> Void) {
    if BecomeDigitalSDK.handleEventsForBackgroundURLSession(
        identifier, completionHandler: completionHandler
    ) {
        return
    }

    // Atiende aquí el evento de otra librería, si corresponde.
    completionHandler()
}
```

Si otra librería de tu aplicación atiende el evento, entrégale también su `completionHandler` según las instrucciones de esa integración. Cuando la SDK devuelve `true`, ya se encarga de ese evento.

En aplicaciones SwiftUI, incorpora `AppDelegate` mediante `@UIApplicationDelegateAdaptor`. iOS determina cuándo puede continuar una transferencia en segundo plano; este comportamiento no garantiza que la verificación termine mientras la aplicación está cerrada. Compruébalo en un dispositivo físico antes de publicar.
