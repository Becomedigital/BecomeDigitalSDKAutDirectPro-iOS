# Configuración de la protección contra capturas de pantalla en iOS

Esta guía corresponde al `BDIdentityVerification.xcframework` incluido en este repositorio.

## Cambio de comportamiento

`BDIVConfig.preventScreenCapture` ahora tiene el valor predeterminado `false`. En versiones distribuidas anteriores, el valor predeterminado era `true`. Si la aplicación omite el parámetro, se permiten las capturas de pantalla y la grabación del contenido de la SDK. El valor predeterminado es el mismo en Debug y Release. Los valores indicados explícitamente conservan el comportamiento solicitado.

| Valor | Comportamiento de la SDK |
| --- | --- |
| `false` (predeterminado) | La SDK no aplica su protección contra capturas ni el bloqueo de grabación a sus pantallas. |
| `true` | La SDK protege sus pantallas contra capturas y muestra una vista de bloqueo mientras detecta una grabación. |

La opción se aplica a las pantallas que presenta la SDK durante el flujo de verificación. No configura otras pantallas de la aplicación anfitriona ni modifica protecciones aplicadas de forma independiente por iOS u otros componentes.

## Activar la protección explícitamente

Indique `preventScreenCapture: true` al crear `BDIVConfig`, antes de llamar a `startVerification()`:

```swift
import BDIdentityVerification

let config = BDIVConfig(
    clienId: "TU_CLIENT_ID",
    clientSecret: "TU_CLIENT_SECRET",
    contractId: "TU_CONTRACT_ID",
    documenTypes: [.DNI, .PASSPORT],
    userId: "TU_USER_ID",
    preventScreenCapture: true
)

let verification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
verification.startVerification()
```

Omita el parámetro o indique `false` para usar el nuevo valor predeterminado. El valor de `preventScreenCapture` queda fijo para cada instancia de `BDIVConfig`; cree otra configuración si un flujo posterior necesita un valor diferente. La opción está disponible para `.Onboarding` y `.Authentication`.

## Migración desde un XCFramework anterior

1. Revise cada creación de `BDIVConfig` en la aplicación. Las llamadas que omiten `preventScreenCapture` pasan de tener protección a permitir capturas al integrar este XCFramework.
2. Agregue `preventScreenCapture: true` donde deba mantenerse la protección anterior. Las llamadas que ya indican `true` o `false` no requieren cambios.
3. Recompile la aplicación con este XCFramework. Intégrelo y fírmelo en el target de la aplicación según el [README](README.md).
4. En un dispositivo físico, compruebe las capturas de pantalla y la grabación durante la captura del documento, la prueba de vida, la cancelación y el regreso a la aplicación. Si la aplicación admite ambos modos, pruebe el valor predeterminado y el valor `true`.

La aplicación integradora debe elegir esta configuración según sus requisitos de privacidad. El parámetro controla las pantallas de la SDK; no reemplaza las políticas de tratamiento de datos ni la protección general de la aplicación.
