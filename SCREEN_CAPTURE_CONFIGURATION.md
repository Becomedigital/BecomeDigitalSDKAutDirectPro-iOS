# Protección de pantalla en iOS

`preventScreenCapture` permite elegir la protección de las pantallas presentadas por la SDK durante la verificación.

| Valor | Comportamiento |
| --- | --- |
| `false`, predeterminado | Permite capturas y grabación sin aplicar la protección de la SDK. |
| `true` | Activa la protección frente a capturas y presenta una vista de bloqueo al detectar grabación. |

La opción se aplica a los dos flujos de verificación y no modifica otras pantallas de tu aplicación. Las restricciones del dispositivo o de otros componentes pueden seguir aplicándose.

## Activar la protección

Define el valor antes de iniciar la verificación:

```swift
let config = BDIVConfig(
    clienId: clientId,
    clientSecret: clientSecret,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId,
    preventScreenCapture: true
)
```

Inicia la SDK con esta configuración según la [guía de integración](README.md#iniciar-una-verificación). Para cambiar la opción en una verificación posterior, crea otra instancia de `BDIVConfig`.

## Al actualizar tu integración

En entregas anteriores, omitir el parámetro activaba la protección. En esta entrega, su valor predeterminado es `false`. Indica `preventScreenCapture: true` si tu aplicación necesita conservar la protección anterior.

Comprueba en un dispositivo físico las capturas, la grabación y el regreso a tu aplicación. Elige esta opción de acuerdo con los requisitos de privacidad de tu integración.
