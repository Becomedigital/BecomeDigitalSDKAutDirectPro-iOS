# Instalación manual de Become para iOS

Esta guía corresponde a la integración por archivo de la candidata `3.5.1-rc.1`. Descarga los binarios desde [Releases](https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro-iOS/releases/tag/3.5.1-rc.1). Para integrar mediante el gestor de paquetes, sigue la [instalación recomendada](INSTALACION.md).

## Requisitos

| Requisito | Versión o condición |
| --- | --- |
| SDK de Become incluida | 3.5.1 |
| Sistema operativo | iOS 16.0 o posterior |
| Destinos incluidos | iPhone físico (`arm64`) y simuladores en Mac con Apple Silicon (`arm64`) o Intel (`x86_64`) |
| Compilador Swift | 6.4 o posterior compatible |
| Amplify Swift | 2.53.3 |
| Amplify UI Swift Liveness | 1.4.4 |
| CaptureCore y CaptureUX | 1.4.3 |
| Licencia de captura | Emitida para el identificador de tu aplicación |

La integración de este paquete se verificó con Xcode 27.2.

Necesitas un JWT vigente y el identificador del contrato. La firma anterior con credenciales continúa disponible para integraciones existentes y está marcada como deprecada; consulta la [guía de inicialización](README.md#iniciar-una-verificación). Esta entrega está preparada para producción. Realiza las pruebas de cámara, documentos y rostro en un dispositivo físico; el paquete también incluye compatibilidad con simuladores para integrar las pantallas.

## Instalación

1. Agrega `BDIdentityVerification.xcframework` al destino de tu aplicación en Xcode y selecciona **Embed & Sign**.
2. En **File > Add Package Dependencies**, agrega los siguientes paquetes con la opción **Exact Version**.

| Paquete | Versión | Producto que debes agregar |
| --- | --- | --- |
| https://github.com/aws-amplify/amplify-swift | 2.53.3 | `Amplify` |
| https://github.com/aws-amplify/amplify-ui-swift-liveness | 1.4.4 | `FaceLiveness` |
| https://github.com/BlinkID/capture-core-sp | 1.4.3 | `CaptureCore` |
| https://github.com/BlinkID/capture-ux-sp | 1.4.3 | `CaptureUX` |

3. Comprueba que `BDIdentityVerification.framework`, `CaptureCore.framework` y `CaptureUX.framework` estén configurados como **Embed & Sign**. Mantén las versiones de la tabla, incluso cuando tu contrato no solicite una captura facial.
4. Agrega la licencia como **`com.become.document.key.txt`**, con pertenencia al destino de tu aplicación e incluida en **Copy Bundle Resources**. El identificador de la aplicación debe coincidir con el autorizado en la licencia.

Si tu aplicación ya incluye alguno de estos paquetes, utiliza una única versión compatible con esta entrega.

## Permisos

Agrega a `Info.plist` una descripción que explique al usuario por qué necesitas la cámara:

```xml
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceder a la cámara para verificar tu identidad.</string>
```

Si tu contrato utiliza ubicación, agrega también `NSLocationWhenInUseUsageDescription`. Rechazar el permiso de ubicación no bloquea la verificación.

Continúa con el [ejemplo de inicialización](README.md#iniciar-una-verificación).
