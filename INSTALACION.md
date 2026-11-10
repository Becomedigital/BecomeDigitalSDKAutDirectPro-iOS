# Instalación de la SDK de Become

## Requisitos

| Requisito | Versión o condición |
| --- | --- |
| Versión de Become | `3.5.1` |
| Sistema operativo | iOS 16.0 o posterior |
| Destinos incluidos | iPhone físico (`arm64`) y simuladores en Mac con Apple Silicon (`arm64`) o Intel (`x86_64`) |
| Compilador Swift | 6.4 o posterior compatible |
| Licencia de captura | Emitida para el identificador de tu aplicación |

La integración de este paquete se verificó con Xcode 27.2.

Necesitas un JWT vigente y el identificador del contrato. La firma anterior con credenciales continúa disponible para integraciones existentes y está marcada como deprecada; consulta la [guía de inicialización](README.md#iniciar-una-verificación). Esta entrega está preparada para producción. Realiza las pruebas de cámara, documentos y rostro en un dispositivo físico; el paquete también incluye compatibilidad con simuladores para integrar las pantallas.

## Instalación

1. En Xcode, abre **File > Add Package Dependencies**.
2. Agrega `https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro-iOS`.
3. Selecciona **Exact Version** e ingresa `3.5.1`.
4. Agrega el producto **BDIdentityVerification** al destino de tu aplicación.

SPM descarga el XCFramework y resuelve automáticamente sus dependencias. La instalación conserva el uso de `import BDIdentityVerification` y los parámetros públicos de inicialización. Si tu aplicación ya utiliza paquetes compartidos, compara sus reglas con la [guía de dependencias y compatibilidad](DEPENDENCIAS.md).

Agrega la licencia como **`com.become.document.key.txt`**, con pertenencia al destino de tu aplicación e incluida en **Copy Bundle Resources**. El identificador de tu aplicación debe coincidir con el autorizado en la licencia.

La versión oficial está disponible en [Releases](https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro-iOS/releases/tag/3.5.1). Realiza la validación funcional en un dispositivo físico.

Si actualizas una integración por archivo, sigue primero la [guía de migración](MIGRACION.md) para evitar módulos duplicados.

## Permisos

Agrega a `Info.plist` una descripción que explique al usuario por qué necesitas la cámara:

```xml
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceder a la cámara para verificar tu identidad.</string>
```

Si tu contrato utiliza ubicación, agrega también `NSLocationWhenInUseUsageDescription`. Rechazar el permiso de ubicación no bloquea la verificación.

Continúa con el [ejemplo de inicialización](README.md#iniciar-una-verificación).

Si prefieres utilizar los binarios descargables, consulta la [integración manual](INSTALACION_MANUAL.md), que requiere configurar sus dependencias por separado.
