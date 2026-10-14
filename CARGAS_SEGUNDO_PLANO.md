# Eventos de segundo plano — iOS

Si su app admite continuar una verificación al pasar a segundo plano, reenvíe los eventos del sistema a la SDK desde `AppDelegate`:

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

    // Reenvíe el evento a otra librería de su app si le corresponde.
    completionHandler()
}
```

En una app SwiftUI, incorpore `AppDelegate` mediante `@UIApplicationDelegateAdaptor`. iOS determina cuándo puede continuar el trabajo en segundo plano. Pruebe el comportamiento en un dispositivo físico antes de publicar.
