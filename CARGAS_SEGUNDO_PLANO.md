# Cargas en redes lentas y segundo plano — iOS

El framework prepara las imágenes fuera del hilo principal y realiza las cargas multipart mediante una sesión de segundo plano. Permite datos móviles y hasta **15 minutos por transferencia**, con timeout de petición de **120 segundos**. No reduce ni recorta las imágenes.

## Integración

Agregue este método a su `AppDelegate` después de reemplazar el XCFramework:

```swift
import UIKit
import BDIdentityVerification

func application(_ application: UIApplication,
                 handleEventsForBackgroundURLSession identifier: String,
                 completionHandler: @escaping () -> Void) {
    if BecomeDigitalSDK.handleEventsForBackgroundURLSession(
        identifier, completionHandler: completionHandler
    ) {
        return // La SDK llamará al completionHandler al terminar de procesar los eventos.
    }

    // Si otra librería administra esta sesión, remita el evento a su propietario.
    // Solo si no hay otro propietario:
    completionHandler()
}
```

Con `SceneDelegate`, el método sigue en `AppDelegate`. En apps SwiftUI, incorpore ese delegado mediante `@UIApplicationDelegateAdaptor`. No necesita habilitar Background Fetch.

## Comportamiento y límites

- Minimizar o bloquear el teléfono no cancela una carga ya entregada al sistema. iOS decide cuándo ejecutarla.
- El polling no inicia nuevas consultas mientras la app está en segundo plano y continúa al volver; conserva los límites configurados.
- La SDK utiliza archivos privados protegidos, excluidos de backups y eliminados al finalizar o fallar la transferencia.
- Cerrar forzosamente la app puede cancelar la carga. Si iOS termina el proceso, se pueden recibir eventos de la sesión, pero la SDK no reconstruye la pantalla ni los callbacks de la verificación anterior.
- Ante un resultado incierto, consulte el estado de la identidad antes de crear otro proceso. No se garantiza una única ejecución en el servidor ante reintentos de transporte.

Antes de publicar su app, pruebe en un iPhone físico con red lenta, sin el debugger conectado, minimizando y bloqueando el teléfono durante la carga.
