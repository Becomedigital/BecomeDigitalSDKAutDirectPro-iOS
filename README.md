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

## Cambios incluidos en esta versión

* `Onboarding` y `Authentication` leen pasos y políticas de `GET /api/v1/sdk-config`; la interfaz SwiftUI conserva la coordinación nativa de captura y navegación.
* `GET /api/v1/public-config` define paletas, componentes, branding, textos y alineación. El host elige `themeMode`; el logo proviene de `branding.logo.url`.
* La selección de país usa una pantalla completa con búsqueda y banderas. Los textos y botones de la SDK usan el tema del contrato con contraste legible.
* El delegado entrega `BDIdentityVerificationResponse` directamente, con objetos públicos opcionales `onboarding`, `authentication` y `verification`; se eliminó `responseDictionary`.
* Se conservan HTTP 201 de `newIdentity`, polling opcional, carga multipart en segundo plano y logs seguros optativos.

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

Importe `BDIdentityVerification`. `BecomeDigitalSDK` es la clase pública; el delegado debe ser un `UIViewController` que implemente `BDIVDelegate`.

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
        switch bdivResult.responseStatus {
        case .SUCCES:
            if let accepted = bdivResult.onboarding {
                // newIdentity aceptó la creación cuando el polling está desactivado.
            }
            if let checked = bdivResult.verification {
                // Polling completado: checked.urlGetData.
            }
            if let match = bdivResult.authentication {
                // Evalúe match.result por separado del éxito HTTP.
            }
        case .ERROR, .PENDING, .NOFOUND:
            break
        }
    }

    func BDIVResponseError(error: String) {
        // Muestre una salida segura; no registre datos personales.
    }
}
```

Conserve `identityVerification` durante la ejecución. Los nombres `clienId` y `documenTypes` se mantienen por compatibilidad pública.

### Parámetros que controla la app

| Parámetro | Tipo y valor predeterminado | Uso |
| --- | --- | --- |
| `clienId`, `clientSecret`, `contractId`, `userId` | `String`, requeridos | Credenciales, contrato e identificador del usuario. |
| `documenTypes` | `[DocumentType]`, requerido en onboarding | Acota documentos del contrato: `.DNI`, `.PASSPORT`, `.DRIVERLICENSE`. Authentication admite `[]`. |
| `flow` | `.Onboarding` | `.Onboarding` o `.Authentication`. |
| `performVerificationCheck` | `true` | Espera el resultado posterior a `newIdentity` cuando corresponde. |
| `pollingMaxAttempts` | `0` | Límite de consultas; `0` conserva intentos ilimitados. |
| `pollingTimeout` | `2` segundos | Timeout de cada GET de polling; no cambia el intervalo. |
| `debugLogsEnabled` | `false` | Habilita diagnósticos seguros antes de iniciar. |
| `preventScreenCapture` | `false` | Cuando es `true`, bloquea capturas y grabaciones mientras se muestra la SDK. |
| `country`, `state` | `nil` | País ISO de dos letras y, para EE. UU., estado precargado. |
| `nationalIdType`, `nationalIdTypeChoices`, `documentNumber` | `nil` / `[]` | Valores documentales precargados, sujetos a las políticas del contrato. |
| `themeMode` | `.system` | `.light`, `.dark` o `.system`, elegido por la app. |

`BDIVConfig` no admite `customerLogo`, `customLocalizationFileName`, colores, URL base ni políticas de captura. Para usar una tabla `Localizable.strings` propia, inclúyala en el target de la app; no se selecciona mediante un parámetro de la SDK.

## Configuración del contrato y presentación

La SDK consulta `GET /api/v1/sdk-config` y `GET /api/v1/public-config` con la sesión del cliente. `.Onboarding` selecciona `flows.onboarding`; `.Authentication`, `flows.reverification`. Las políticas y el orden del contrato determinan introducción, ATDP, contacto, país, tipo documental, captura y liveness. El contrato decide modo de captura, reverso, holograma, implementación facial, umbrales y revisión de selfie. Si queda un solo documento permitido, se muestra seleccionado para informar qué se capturará. La selección de país tiene búsqueda en la misma pantalla y solicita estado para EE. UU. cuando corresponde.

`public-config` aporta `theming`, `components`, `branding`, `texts` y `ui`: paletas, tipografía, densidad, radios, alineación, componentes, logo y textos. `themeMode` no forma parte de ese JSON; `.system` sigue la preferencia del dispositivo. El logo se carga de `branding.logo.url` para la ejecución actual sin conservarlo en caché. Los colores de texto se ajustan cuando el contraste con el fondo es insuficiente.

Los textos se resuelven por `texts.{locale}.{namespace}.{clave}`. Una clave ausente recurre a `es` y después al valor predeterminado de la SDK. Los valores nativos que la app incluya en `Localizable.strings` tienen prioridad para esa frase. [Mapa de claves y localización](LOCALIZACION.md). El parámetro web `webhookUrl` no se envía desde mobile.

El XCFramework de este repositorio apunta a **producción** (`https://api.svi.becomedigital.net`). El ambiente está incorporado en ambas slices y no puede cambiarse con `BDIVConfig`. El repositorio fuente genera un paquete `dev` separado para pruebas internas contra `https://api.dev.svi.becomedigital.net`.

## Flujos y objetos de respuesta

### Onboarding

Con `performVerificationCheck: false`, `POST /api/v1/newIdentity` se considera exitoso con HTTP 201 y el delegado recibe `onboarding: BDIVOnboardingResult?` con `code`, `message`, `urlResource` y `userId`, todos opcionales. Esto indica creación aceptada, no aprobación biométrica final.

Con `performVerificationCheck: true` (predeterminado), la SDK conserva el polling y al finalizar entrega `verification: BDIVVerificationResult?` con `urlGetData`. Las consultas se programan cada 4 segundos; `pollingTimeout` rige cada GET y `pollingMaxAttempts` limita el total. Un límite positivo agotado presenta un reintento en la SDK.

```swift
let config = BDIVConfig(
    clienId: clientId, clientSecret: clientSecret, contractId: contractId,
    documenTypes: [.DNI], userId: userId,
    performVerificationCheck: false,
    pollingMaxAttempts: 0, pollingTimeout: 2
)
```

### Authentication

`.Authentication` selecciona `reverification` y, según el contrato, ejecuta liveness y `POST /api/v1/matches`. Puede usar `documenTypes: []`. Un HTTP exitoso entrega `.SUCCES` aun cuando `authentication?.result == false`; ese booleano es el resultado de negocio y debe evaluarse por separado. `BDIVAuthenticationResult` expone `company`, `confidence`, `executionId`, `liveness` y `userId` como opcionales, y `result` como `Bool`.

```swift
let config = BDIVConfig(
    clienId: clientId, clientSecret: clientSecret, contractId: contractId,
    documenTypes: [], userId: userId, flow: .Authentication
)
```

Solo se llena el objeto de respuesta que corresponde al flujo y al modo de respuesta. `BDIdentityVerificationResponse` contiene `responseStatus`, `message`, `onboarding`, `authentication` y `verification`; el delegado ya recibe ese tipo directamente. `toJson()` está disponible para interoperabilidad, pero evite registrar datos personales. Los errores terminales se entregan por `BDIVResponseError(error:)` y las cancelaciones utilizan ese callback con el texto de cancelación. [Catálogo de errores](ERRORES.md).

## Localización y diagnósticos

Agregue [Localizable.strings](Localizable.strings) al target y cambie únicamente las claves que requiera. La app prevalece para esas claves sobre el contrato; las restantes conservan el valor del contrato o el predeterminado. [Guía de localización](LOCALIZACION.md).

`debugLogsEnabled: true` activa eventos seguros `BecomeSDK` sin credenciales, imágenes ni respuestas completas; está desactivado por defecto. [Guía de logs](LOGGING.md).

## Captura y carga documental

La SDK envía las imágenes originales completas del frente y, cuando corresponde, del reverso; la imagen recortada se usa para vista previa. Las cargas multipart pueden continuar en segundo plano hasta 15 minutos por transferencia. La app debe reenviar al SDK los eventos de sesión de fondo desde `AppDelegate`: [guía de integración](CARGAS_SEGUNDO_PLANO.md). `pollingTimeout` solo se aplica a las consultas GET del resultado.

La app debe declarar `NSCameraUsageDescription`. Si el contrato habilita GPS opcional, declare también `NSLocationWhenInUseUsageDescription`; una denegación de ubicación no bloquea el flujo.

## Requisitos

* **iOS 17.0 o superior**, según `MinimumOSVersion` de la slice de dispositivo incluida.
* Las dependencias de Amplify y Microblink indicadas arriba, con licencias y permisos de cámara correspondientes.
* Integrar el XCFramework con **Embed & Sign** y firmar el framework dentro de la app.

## Procedencia del artefacto

Este XCFramework se generó desde `iOS_become_sdk` en `feature/mobile-contract-parity` (commit `afbec9a`), esquema `BDIdentityVerification_PROD` / `Release`. SHA-256 de la slice de dispositivo: `4f754913605881743287e3e84b11f956fdc16c81fcf97a4a098ad6770de92a39`. La slice de simulador conserva `arm64` y `x86_64`; se eliminaron sus símbolos de depuración para mantener cada archivo por debajo del límite de GitHub y se volvió a firmar. SHA-256 de su ejecutable: `717d0c9c8ed46da0335f6210613ce5cd6fbbdfc83769c83c0bfde598061771f3`.
