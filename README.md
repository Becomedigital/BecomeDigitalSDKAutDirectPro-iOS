# SDK de Become para iOS

Integra la verificación de identidad de Become en tu aplicación. La SDK presenta las pantallas de captura y devuelve el resultado mediante objetos que tu aplicación puede consultar.

El [proyecto de ejemplo con SwiftUI](Examples/SwiftUIDemo/README.md) muestra una integración completa desde la pantalla de la aplicación hasta la configuración y las respuestas de la SDK. Para ejecutar una verificación necesitas credenciales y una licencia de captura emitidas para tu contrato y el identificador de tu aplicación.

Puedes iniciar dos flujos:

- **Onboarding:** registro y verificación de una identidad.
- **Authentication:** autenticación de un usuario existente.

Los pasos, documentos admitidos, apariencia y textos de la verificación corresponden al contrato de tu organización.

## Contenido de la guía

- [Requisitos](INSTALACION.md#requisitos)
- [Instalación](INSTALACION.md#instalación)
- [Permisos](INSTALACION.md#permisos)
- [Iniciar una verificación](#iniciar-una-verificación)
- [Configurar la SDK](#configurar-la-sdk)
- [Consultar el resultado](#consultar-el-resultado)
- [Apariencia e idioma](#apariencia-e-idioma)
- [Ejemplo práctico con SwiftUI](#ejemplo-práctico-con-swiftui)
- [Guías complementarias](#guías-complementarias)

## Antes de comenzar

Necesitas una aplicación para iOS 16.0 o posterior, las credenciales de tu integración, el identificador del contrato y la licencia de captura correspondiente a tu aplicación. Sigue la [guía de instalación](INSTALACION.md) para agregar la SDK, sus dependencias y permisos.

## Iniciar una verificación

Implementa `BDIVDelegate` en el controlador que presenta la SDK y conserva la instancia mientras el flujo permanezca activo.

```swift
import UIKit
import BDIdentityVerification

final class VerificacionViewController: UIViewController, BDIVDelegate {
    private var verificacion: BecomeDigitalSDK?

    func iniciarOnboarding() {
        let config = BDIVConfig(
            clienId: "TU_CLIENT_ID",
            clientSecret: "TU_CLIENT_SECRET",
            contractId: "TU_CONTRACT_ID",
            documenTypes: [.DNI, .PASSPORT, .DRIVERLICENSE],
            userId: "TU_USER_ID",
            flow: .Onboarding,
            themeMode: .system
        )
        verificacion = BecomeDigitalSDK(bdivConfig: config, delegate: self)
        verificacion?.startVerification()
    }

    func BDIVResponseSuccess(bdivResult: BDIdentityVerificationResponse) {
        guard bdivResult.responseStatus == .SUCCES else {
            // Presenta el estado recibido sin asumir una aprobación.
            return
        }
        if let resultado = bdivResult.authentication {
            if resultado.result {
                // Continúa con la autenticación aprobada.
            } else {
                // Informa que la autenticación no fue aprobada.
            }
        } else if let resultado = bdivResult.verification {
            _ = resultado.urlGetData
            // Continúa con el onboarding confirmado.
        } else if let resultado = bdivResult.onboarding {
            _ = resultado.userId
            // El registro fue creado; no representa una aprobación final.
        }
    }

    func BDIVResponseError(error: String) {
        // Recupera la interfaz de tu aplicación y permite un nuevo intento.
    }
}
```

Utiliza los identificadores `clienId`, `documenTypes` y `SUCCES` exactamente como aparecen en los ejemplos.

### Autenticar a un usuario existente

Crea una configuración con `flow: .Authentication` y el `userId` del usuario que deseas autenticar. Puedes indicar `documenTypes: []` cuando el flujo no requiera documentos. El inicio y los métodos del delegado son los mismos del ejemplo anterior.

## Configurar la SDK

Define los parámetros de `BDIVConfig` antes de iniciar la verificación.

| Parámetro | Valor predeterminado | Uso |
| --- | --- | --- |
| `clienId`, `clientSecret`, `contractId` | Obligatorios | Credenciales de tu integración e identificador del contrato. No deben estar vacíos. |
| `userId` | Argumento obligatorio | Identificador del usuario. En onboarding puede ser una cadena vacía; en autenticación debe identificar a un usuario existente. |
| `documenTypes` | Argumento obligatorio | Tipos de documento: `.DNI`, `.PASSPORT` y `.DRIVERLICENSE`. Un arreglo vacío utiliza los disponibles en el contrato. |
| `flow` | `.Onboarding` | Flujo que deseas iniciar: `.Onboarding` o `.Authentication`. |
| `performVerificationCheck` | `true` | Espera la confirmación del onboarding. Con `false`, devuelve el resultado de creación. |
| `pollingMaxAttempts` | `0` | Número máximo de consultas del resultado. `0` permite seguir esperando sin límite de intentos. |
| `pollingTimeout` | `2` segundos | Tiempo máximo de espera por consulta del resultado. No es el tiempo máximo del flujo completo. |
| `debugLogsEnabled` | `false` | Activa los mensajes de diagnóstico para soporte. |
| `preventScreenCapture` | `false` | Activa la protección de las pantallas de la SDK frente a capturas y grabación. |
| `country` | `nil` | Código de país de dos letras, como `CO`, o varios códigos separados por comas. |
| `state` | `nil` | Código de estado de Estados Unidos, cuando corresponda. |
| `nationalIdType` | `nil` | Subtipo de identificación precargado. |
| `nationalIdTypeChoices` | `[]` | Opciones de subtipo de identificación. |
| `documentNumber` | `nil` | Número de documento precargado. |
| `themeMode` | `.system` | Apariencia `.light`, `.dark` o la preferencia del dispositivo con `.system`. |

Los valores de la configuración quedan fijos para esa instancia. Crea otra configuración para iniciar una verificación con parámetros diferentes.

### Espera del resultado

Con `performVerificationCheck: true`, la SDK mantiene la espera mientras el resultado siga pendiente. Si necesitas limitarla, indica un valor positivo en `pollingMaxAttempts` y atiende el error mediante el delegado. Puedes aumentar `pollingTimeout`, por ejemplo a `30`, cuando la conexión requiera más tiempo por consulta.

Con `performVerificationCheck: false`, recibirás el resultado de creación sin esperar la confirmación final.

### Selección de documentos

La SDK combina los tipos solicitados con los admitidos por el contrato. Si no hay coincidencias, utiliza los del contrato. Cuando solo existe un tipo, también lo muestra para que el usuario confirme qué documento va a capturar.

El pasaporte requiere la cara frontal. Los demás documentos solicitan los lados definidos para el contrato. La vista previa puede mostrar un recorte; la verificación utiliza la captura completa. Si el contrato solo requiere documentos, no se exige una captura facial.

## Consultar el resultado

`BDIVResponseSuccess` recibe un `BDIdentityVerificationResponse` con `responseStatus`, `message` y objetos opcionales según la operación:

| Propiedad | Tipo | Contenido |
| --- | --- | --- |
| `onboarding` | `BDIVOnboardingResult?` | `code`, `message`, `urlResource`, `userId`. Disponible al devolver la creación sin esperar la confirmación final. |
| `verification` | `BDIVVerificationResult?` | `urlGetData`. Disponible con el resultado confirmado del onboarding. |
| `authentication` | `BDIVAuthenticationResult?` | `company`, `confidence`, `executionId`, `liveness`, `result`, `userId`. Consulta `result` para decidir si la autenticación fue aprobada. |

Consulta cada propiedad de forma opcional. El resultado de creación no implica una aprobación final. En autenticación, recibir `.SUCCES` indica que la operación devolvió un resultado; la decisión está en `authentication.result`.

Los estados declarados son `SUCCES`, `ERROR`, `PENDING` y `NOFOUND`. El objeto también ofrece `toJson()` si necesitas una representación en texto. Los errores y la cancelación del usuario se comunican mediante `BDIVResponseError(error:)`.

El contenido de `message` y `error` es descriptivo y puede cambiar con el idioma; no lo utilices como código para tomar decisiones. Consulta la [guía de resultados y errores](ERRORES.md).

## Apariencia e idioma

La SDK utiliza el logo, colores, tipografía y textos asociados al contrato. En la aplicación puedes elegir el modo claro, oscuro o del sistema con `themeMode`.

Las indicaciones de captura y algunos mensajes de carga y conexión admiten traducciones locales. Consulta las claves y los ejemplos en la [guía de localización](LOCALIZACION.md).

## Ejemplo práctico con SwiftUI

El [proyecto de ejemplo](Examples/SwiftUIDemo/README.md) incluye el puente entre SwiftUI y `BDIVDelegate`, el ciclo de vida con escenas, la atención de sesiones en segundo plano y recursos de localización. Puedes compilarlo sin credenciales para revisar la integración; sigue su guía para agregar tus datos y tu licencia de forma local antes de probar el flujo en un dispositivo físico.

## Guías complementarias

- [Instalación, dependencias, licencia y permisos](INSTALACION.md)
- [Resultados, errores y cancelación](ERRORES.md)
- [Localización y claves disponibles](LOCALIZACION.md)
- [Diagnóstico para soporte](LOGGING.md)
- [Protección de pantalla](SCREEN_CAPTURE_CONFIGURATION.md)
- [Continuidad en segundo plano](CARGAS_SEGUNDO_PLANO.md)
- [Revisión al actualizar la integración](CAMBIOS.md)

Antes de publicar tu aplicación, comprueba en un dispositivo físico los permisos, la licencia, los documentos solicitados, la cancelación y el manejo del resultado de cada flujo que utilices.
