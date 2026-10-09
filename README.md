# Documentación del SDK de Become iOS

## Descripción general

El SDK de Become para iOS permite ejecutar procesos de verificación de identidad dentro de una aplicación nativa. Para que el flujo funcione correctamente, es necesario integrar el framework principal de Become junto con las dependencias de **AWS Amplify Face Liveness** y **Microblink**.

Estas librerías permiten habilitar correctamente:

* Captura de documentos
* Flujo de cámara
* Validación facial
* Face Liveness
* Componentes de captura de Microblink

---

## Funciones públicas

- Flujos de onboarding y autenticación con respuestas tipadas.
- Selección de país con búsqueda, captura documental y verificación facial según el flujo disponible.
- Interfaz SwiftUI adaptada a la identidad visual del contrato.
- Modo visual elegible mediante `themeMode` y textos personalizables con `Localizable.strings`.

---

## Versiones requeridas

El XCFramework incluido fue generado y validado con estas versiones exactas:

* **Become iOS SDK**: `1.2.3`
* **Amplify Swift**: `2.58.5`
* **Amplify UI Swift Liveness**: `1.4.5`
* **BlinkID Capture Core**: `1.4.3`
* **BlinkID Capture UX**: `1.4.3`

Referencias de la versión de captura integrada:

* [Guía de integración Capture iOS 1.4.3](https://github.com/BlinkID/capture-ios/tree/v1.4.3)
* [Notas de versión de Capture iOS 1.4.3](https://github.com/BlinkID/capture-ios/blob/v1.4.3/Release_notes.md)
* [CaptureCore 1.4.3](https://github.com/BlinkID/capture-core-sp/tree/v1.4.3)
* [CaptureUX 1.4.3](https://github.com/BlinkID/capture-ux-sp/tree/v1.4.3)

---

## Agregar licencias al proyecto

Agregue los archivos de licencia proporcionados para la inicialización del SDK y la captura de documentos.

### Archivos requeridos

* **com.become.document.key.txt**

Este archivo debe estar incluido en los recursos del proyecto y en el target correspondiente.

<p align="center">
  <img src="https://github.com/Becomedigital/become_IOS_SDK/blob/master/IMG_4.png">
</p>

### Importante

Asegúrese de que el [`Bundle Identifier`](https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids) del proyecto coincida con la licencia asignada al cliente.

---

## Agregar el framework de Become al proyecto

1. Agregue el archivo **BDIdentityVerification.xcframework** a su proyecto.
2. Verifique que quede incluido en la sección **Frameworks, Libraries, and Embedded Content** dentro de la configuración del target en Xcode.
3. Seleccione **Embed & Sign** para que la aplicación firme el framework al integrarlo.

---

## Integración con Swift Package Manager

Además del framework de Become, es necesario agregar las dependencias externas requeridas por el SDK.

### 1. Agregar paquetes

Abra su proyecto en Xcode y vaya a:

**File > Add Packages**

![Agregar dependencia del paquete Amplify](https://github.com/user-attachments/assets/f845c6f2-d235-43a8-a1e3-a796cc1426a4)

### 2. Registrar las URLs de los paquetes

Agregue las siguientes URLs:

```text
https://github.com/aws-amplify/amplify-swift
https://github.com/aws-amplify/amplify-ui-swift-liveness
https://github.com/BlinkID/capture-core-sp
https://github.com/BlinkID/capture-ux-sp
```

### 3. Configurar versiones

Para reproducir la combinación con la que fue generado el XCFramework, seleccione `Exact Version`:

* **amplify-swift** → `2.58.5`
* **amplify-ui-swift-liveness** → `1.4.5`
* **capture-core-sp** → `1.4.3`
* **capture-ux-sp** → `1.4.3`

---

## Configuración en `Info.plist`

El SDK requiere permisos de acceso a la cámara. Agregue la siguiente clave en su `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Requerimos acceso a la cámara para propósitos de verificación de identidad.</string>
```

---

## Inicialización del SDK

Importe `BDIdentityVerification`. El delegado debe ser un `UIViewController` que implemente `BDIVDelegate`. Conserve la instancia de `BecomeDigitalSDK` durante la ejecución.

```swift
import UIKit
import BDIdentityVerification

final class ViewController: UIViewController, BDIVDelegate {
    private var identityVerification: BecomeDigitalSDK?

    func iniciar() {
        let config = BDIVConfig(
            clienId: "TU_CLIENT_ID",
            clientSecret: "TU_CLIENT_SECRET",
            contractId: "TU_CONTRACT_ID",
            documenTypes: [.DNI, .PASSPORT],
            userId: "TU_USER_ID",
            flow: .Onboarding,
            themeMode: .system
        )
        identityVerification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
        identityVerification?.startVerification()
    }

    func BDIVResponseSuccess(bdivResult: BDIdentityVerificationResponse) {
        guard bdivResult.responseStatus == .SUCCES else { return }
        if let started = bdivResult.onboarding { _ = started.userId }
        if let final = bdivResult.verification { _ = final.urlGetData }
        if let authentication = bdivResult.authentication {
            // Evalúe authentication.result por separado.
            _ = authentication.result
        }
    }

    func BDIVResponseError(error: String) {
        // Restaure la pantalla de la app y permita un nuevo inicio.
    }
}
```

Los nombres públicos `clienId` y `documenTypes` se conservan por compatibilidad.

### Parámetros públicos

| Parámetro | Predeterminado | Uso |
| --- | --- | --- |
| `clienId`, `clientSecret`, `contractId`, `userId` | Requeridos | Identifican al cliente, contrato y usuario. |
| `documenTypes` | Requerido en onboarding | `.DNI`, `.PASSPORT`, `.DRIVERLICENSE`; en autenticación admite `[]`. |
| `flow` | `.Onboarding` | `.Onboarding` o `.Authentication`. |
| `performVerificationCheck` | `true` | Espera el resultado final de onboarding antes de devolverlo. |
| `pollingMaxAttempts` | `0` | Límite de intentos de espera; `0` no establece límite. |
| `pollingTimeout` | `2` segundos | Tiempo máximo de cada intento de espera. |
| `debugLogsEnabled` | `false` | Activa diagnósticos durante una prueba. |
| `preventScreenCapture` | `false` | Protege el contenido mostrado por la SDK cuando es `true`. |
| `country`, `state` | `nil` | País de dos letras y estado precargado para EE. UU. |
| `nationalIdType`, `nationalIdTypeChoices`, `documentNumber` | Vacíos | Datos documentales precargados, si corresponden. |
| `themeMode` | `.system` | `.light`, `.dark` o `.system`. |

La SDK presenta los pasos y la identidad visual asignados al contrato. El host solo elige el modo claro u oscuro; colores, logo, contenido y diseño no se configuran en `BDIVConfig`. Las frases pueden personalizarse con el [archivo de localización](Localizable.strings) y la [guía de claves](LOCALIZACION.md).

## Respuestas

`BDIVResponseSuccess` entrega `BDIdentityVerificationResponse`, con `responseStatus`, `message` y estos objetos opcionales:

| Objeto | Campos públicos | Cuándo consultarlo |
| --- | --- | --- |
| `onboarding` | `code`, `message`, `urlResource`, `userId` | Onboarding con `performVerificationCheck=false`; indica que se inició el proceso, no que haya sido aprobado. |
| `verification` | `urlGetData` | Onboarding con espera del resultado final. |
| `authentication` | `company`, `confidence`, `executionId`, `liveness`, `result`, `userId` | Autenticación. Evalúe `result` por separado de `responseStatus`. |

Para autenticación use `flow: .Authentication` y, si no corresponde capturar documentos, `documenTypes: []`. Los errores y cancelaciones llegan a `BDIVResponseError(error:)`; consulte [manejo de errores](ERRORES.md).

## Permisos y diagnóstico

La app debe declarar `NSCameraUsageDescription`. Si utiliza ubicación, declare también `NSLocationWhenInUseUsageDescription`.

`debugLogsEnabled: true` habilita diagnósticos para una prueba; desactívelos al terminar. [Guía de logs](LOGGING.md).

Si su app gestiona eventos de segundo plano, implemente el método público indicado en [integración de segundo plano](CARGAS_SEGUNDO_PLANO.md).

## Requisitos

- iOS 17.0 o superior.
- Las dependencias y licencias indicadas arriba.
- Integrar el XCFramework con **Embed & Sign**.
