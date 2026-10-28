# Instalación de la SDK de Become

## Requisitos

| Requisito | Versión o condición |
| --- | --- |
| SDK de Become incluida | 1.2.3 |
| Sistema operativo | iOS 16.0 o posterior |
| Xcode | 27.0 o posterior compatible |
| Amplify Swift | 2.53.3 |
| Amplify UI Swift Liveness | 1.4.4 |
| CaptureCore y CaptureUX | 1.4.3 |
| Licencia de captura | Emitida para el identificador de tu aplicación |

Necesitas las credenciales y el identificador de contrato entregados por Become. Esta entrega está preparada para producción. Realiza las pruebas de cámara, documentos y rostro en un dispositivo físico; el paquete también incluye compatibilidad con simuladores para integrar las pantallas.

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
