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

* Selección de flujo mediante `flow`: `.Onboarding` o `.Authentication`.
* Control opcional de la consulta del resultado final con `performVerificationCheck`.
* Configuración del número máximo de consultas mediante `pollingMaxAttempts`.
* Configuración del timeout de cada consulta mediante `pollingTimeout`.
* Compatibilidad con `CaptureCore` y `CaptureUX` 1.4.3, incluyendo ajustes de cámara para dispositivos con lente macro.
* Envío de las capturas completas del documento, sin usar la imagen recortada por Microblink.
* `responseDictionary` ahora es opcional en `BDIdentityVerificationResponse`.
* Cuando `newIdentity` informa que no se superó la prueba de vida, la SDK finaliza con error. Para reintentar, la aplicación debe iniciar una instancia nueva del proceso.

---

## Versiones requeridas

El XCFramework incluido fue generado y validado con estas versiones exactas:

* **Become iOS SDK**: `1.2.3`
* **Amplify Swift**: `2.53.3`
* **Amplify UI Swift Liveness**: `1.4.4`
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

* **amplify-swift** → `2.53.3`
* **amplify-ui-swift-liveness** → `1.4.4`
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

### Importar el SDK

```swift
import BDIdentityVerification
```

### Inicializar e iniciar el proceso de verificación

> `BDIdentityVerification` es el nombre del módulo.  
> La clase pública para iniciar el flujo es `BecomeDigitalSDK`.

```swift
let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                            clientSecret: "TU_CLIENT_SECRET",
                            contractId: "TU_CONTRACT_ID",
                            documenTypes: [.DNI, .PASSPORT],
                            userId: "TU_USER_ID",
                            customerLogo: "icon",
                            customLocalizationFileName: "MBLocalizable",
                            performVerificationCheck: true,
                            flow: .Onboarding,
                            pollingMaxAttempts: 0,
                            pollingTimeout: 2)

let identityVerification = BecomeDigitalSDK(bdivConfig: bdivConfig, delegate: self)
identityVerification.startVerification()
```

### Parámetros de `BDIVConfig`

| Parámetro | Tipo | Predeterminado | Descripción |
| --- | --- | --- | --- |
| `clienId` | `String` | Requerido | Identificador entregado al cliente. El nombre público conserva `clienId` por compatibilidad. |
| `clientSecret` | `String` | Requerido | Credencial secreta del cliente. |
| `contractId` | `String` | Requerido | Contrato que define la operación del SDK. |
| `documenTypes` | `[DocumentType]` | Requerido | Documentos disponibles: `.DNI`, `.PASSPORT` y `.DRIVERLICENSE`. Debe contener al menos uno en onboarding. |
| `userId` | `String` | Requerido | Identificador único del usuario. |
| `customerLogo` | `String` | `""` | Nombre del recurso de imagen que se mostrará como logo. |
| `customLocalizationFileName` | `String?` | `"MBLocalizable"` | Nombre del archivo de localización personalizado, sin extensión. |
| `performVerificationCheck` | `Bool` | `true` | Si es `true`, consulta el resultado final. Si es `false`, termina después de decodificar la respuesta de `POST /api/v1/newIdentity`. |
| `flow` | `BDIVConfig.Flow` | `.Onboarding` | Selecciona el flujo completo o solo autenticación facial. |
| `pollingMaxAttempts` | `Int` | `0` | Máximo de consultas del resultado. `0` mantiene consultas ilimitadas. Los valores negativos se normalizan a `0`. |
| `pollingTimeout` | `TimeInterval` | `2` | Timeout en segundos aplicado a cada GET de resultados. Los valores menores o iguales a cero se normalizan a `2`. |

### Tipos de flujo

#### Onboarding

Ejecuta selección y captura de documento, prueba de vida, creación de identidad y, cuando corresponde, consulta del resultado.

```swift
let config = BDIVConfig(clienId: "TU_CLIENT_ID",
                        clientSecret: "TU_CLIENT_SECRET",
                        contractId: "TU_CONTRACT_ID",
                        documenTypes: [.DNI, .PASSPORT, .DRIVERLICENSE],
                        userId: "TU_USER_ID",
                        flow: .Onboarding)
```

#### Authentication

Omite el onboarding y la evaluación de verificaciones anteriores. Ejecuta únicamente la prueba de vida y la autenticación facial mediante `POST /api/v1/matches`. `documenTypes` puede enviarse vacío porque no existe captura documental en este flujo.

```swift
let config = BDIVConfig(clienId: "TU_CLIENT_ID",
                        clientSecret: "TU_CLIENT_SECRET",
                        contractId: "TU_CONTRACT_ID",
                        documenTypes: [],
                        userId: "USUARIO_CON_ONBOARDING_PREVIO",
                        flow: .Authentication)
```

### Consulta del resultado y polling

Con `performVerificationCheck: true`, la SDK usa la URL retornada por `newIdentity` para consultar el resultado. Si debe usar el fallback, consulta `GET /api/v1/identity/<user_id>`.

Las consultas se programan cada 4 segundos. `pollingTimeout` controla el timeout individual de cada GET; no cambia ese intervalo. Si `pollingMaxAttempts` es mayor que cero, al agotarse los intentos la SDK finaliza con error. El valor predeterminado `0` conserva el polling ilimitado.

```swift
let config = BDIVConfig(clienId: "TU_CLIENT_ID",
                        clientSecret: "TU_CLIENT_SECRET",
                        contractId: "TU_CONTRACT_ID",
                        documenTypes: [.DNI],
                        userId: "TU_USER_ID",
                        performVerificationCheck: true,
                        flow: .Onboarding,
                        pollingMaxAttempts: 30,
                        pollingTimeout: 5)
```

Con `performVerificationCheck: false`, no se inicia el polling y se retorna inmediatamente la respuesta decodificada de `newIdentity`:

```swift
let config = BDIVConfig(clienId: "TU_CLIENT_ID",
                        clientSecret: "TU_CLIENT_SECRET",
                        contractId: "TU_CONTRACT_ID",
                        documenTypes: [.DNI],
                        userId: "TU_USER_ID",
                        performVerificationCheck: false)
```

> `POST /api/v1/newIdentity` tiene un timeout fijo de 120 segundos porque carga la prueba de vida y las imágenes completas del documento. `pollingTimeout` solo aplica a las consultas GET del resultado.

---

## Manejo de respuestas del SDK

El SDK responde a través de los métodos del protocolo `BDIVDelegate`.
El callback de éxito entrega un `AnyObject`, y el modelo público documentado por el framework es `BDIdentityVerificationResponse`.

```swift
func BDIVResponseSuccess(bdivResult: AnyObject) {
    if let response = bdivResult as? BDIdentityVerificationResponse {
        print(response.toJson() ?? "")
    } else {
        print(String(describing: bdivResult))
    }
}

func BDIVResponseError(error: String) {
    print(error)
}
```

### Estructura de `BDIdentityVerificationResponse` 

```swift
/// A model representing the response returned after executing the identity verification flow.
/// 
/// This structure holds essential data such as status, descriptive message, and an optional dictionary
/// with additional response values that may be used for further processing.
public struct BDIdentityVerificationResponse {
    
    /// Initializes a new instance of `BDIdentityVerificationResponse` with provided values.
///
/// - Parameters:
///   - message: A textual description of the result.
///   - responseDictionary: An optional dictionary containing additional data returned from the verification process.
///   - responseStatus: The current verification status represented by a `StatusType` value.
    internal init(message: String = "", responseDictionary: [String : Any]? = nil, responseStatus: BDIdentityVerificationResponse.StatusType = .PENDING) {
        self.message = message
        self.responseDictionary = responseDictionary
        self.responseStatus = responseStatus
    }
    
    /// Default initializer for `BDIdentityVerificationResponse`.
    public init() {}
    
    /// Enum representing the different status types for a verification response.
    public enum StatusType: String {
        /// Indicates a successful verification response.
        case SUCCES
        /// Indicates an error occurred during verification.
        case ERROR
        /// Indicates that the verification is still in progress.
        case PENDING
        /// Indicates that the requested verification data was not found.
        case NOFOUND
    }
    
    /// A textual description conveying the result of the identity verification process.
    public var message: String = ""
    
    /// A dictionary containing optional key-value pairs returned as part of the verification response.
    public var responseDictionary: [String : Any]?
    
    /// Indicates the outcome of the identity verification, such as success or failure.
    public var responseStatus: StatusType = .PENDING
    
    public func toJson() -> String? {
        var jsonDict: [String: Any] = [
            "message": message,
            "responseStatus": responseStatus.rawValue
        ]
        
        if let responseDictionary = responseDictionary {
            jsonDict["responseDictionary"] = responseDictionary
        }
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: jsonDict, options: .prettyPrinted)
            return String(data: jsonData, encoding: .utf8)
        } catch {
            print("Failed to convert BDIdentityVerificationResponse to JSON: \(error)")
            return nil
        }
    }
}
```

No fuerce el desempaquetado de `responseDictionary`. Su contenido depende del camino de ejecución y puede ser `nil`:

```swift
func BDIVResponseSuccess(bdivResult: AnyObject) {
    guard let response = bdivResult as? BDIdentityVerificationResponse else { return }

    print("Estado:", response.responseStatus.rawValue)
    print("Mensaje:", response.message)

    if let details = response.responseDictionary {
        print("Detalles:", details)
    }
}
```

Los errores terminales, incluidos un liveness no superado y el agotamiento de los intentos de polling, cierran la interfaz de la SDK y se entregan mediante `BDIVResponseError(error:)`. Para reintentar un liveness rechazado por `newIdentity`, inicie un proceso nuevo.

---

## Errores comunes

### 1. Parámetros requeridos vacíos

Los siguientes parámetros no deben enviarse vacíos:

| Parámetro         | Valor inválido |
| ----------------- | -------------- |
| `clientSecret`    | `""`           |
| `clienId`         | `""`           |
| `contractId`      | `""`           |
| `userId`          | `""`           |
| `documenTypes`    | `[]` en `.Onboarding` |

Error en consola:

```text
parameters cannot be empty
```

### 2. `Incorrect SDK configuration`

Además de validar los parámetros anteriores, la instancia usada como `delegate` debe ser un `UIViewController` que implemente `BDIVDelegate`. Inicie la SDK desde ese controlador:

```swift
final class ViewController: UIViewController, BDIVDelegate {
    // ...
    let identityVerification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
}
```

### 3. Flujo facial no disponible

Si el flujo facial no inicia correctamente, valide que:

* `amplify-swift` esté agregado
* `amplify-ui-swift-liveness` esté agregado
* Las versiones configuradas coincidan con las requeridas
* Las dependencias de Microblink estén incluidas en el target

### 4. Error de compilación: `Cannot call value of non-function type 'module<BDIdentityVerification>'`

Este error ocurre cuando se intenta crear el SDK de esta forma:

```swift
let identityVerification = BDIdentityVerification(...)
```

`BDIdentityVerification` es el nombre del módulo importado, no una clase instanciable.
La forma correcta es:

```swift
import BDIdentityVerification

let identityVerification = BecomeDigitalSDK(bdivConfig: bdivConfig, delegate: self)
identityVerification.startVerification()
```

---

## Ejemplo de implementación

```swift
import UIKit
import BDIdentityVerification

class ViewController: UIViewController {
    private var identityVerification: BecomeDigitalSDK?

    override func viewDidLoad() {
        super.viewDidLoad()
    }

    @IBAction func startAction(_ sender: Any) {
        let dateFormatter = DateFormatter()
        dateFormatter.locale = Locale(identifier: "es_ES")
        dateFormatter.dateFormat = "yyyyMMddHHmmssSSS"
        let userId = dateFormatter.string(from: Date())

        let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                                    clientSecret: "TU_CLIENT_SECRET",
                                    contractId: "TU_CONTRACT_ID",
                                    documenTypes: [.DNI, .DRIVERLICENSE, .PASSPORT],
                                    userId: userId,
                                    customerLogo: "icon",
                                    customLocalizationFileName: "MBLocalizable",
                                    performVerificationCheck: true,
                                    flow: .Onboarding,
                                    pollingMaxAttempts: 30,
                                    pollingTimeout: 5)

        identityVerification = BecomeDigitalSDK(bdivConfig: bdivConfig, delegate: self)
        identityVerification?.startVerification()
    }
}

extension ViewController: BDIVDelegate {
    func BDIVResponseSuccess(bdivResult: AnyObject) {
        if let response = bdivResult as? BDIdentityVerificationResponse {
            print(response.toJson() ?? "")
            if let details = response.responseDictionary {
                print(details)
            }
        } else {
            print(String(describing: bdivResult))
        }
    }

    func BDIVResponseError(error: String) {
        print(error)
    }
}
```

---

## Captura y envío de documentos

La integración usa `CaptureCore` y `CaptureUX` 1.4.3. La SDK configura la cámara para mejorar el enfoque cercano en dispositivos que disponen de cámara macro.

Al completar la captura se envía la imagen original completa (`capturedImage`) del frente y, cuando aplica, del reverso. La imagen transformada o recortada (`transformedImage`) puede utilizarse internamente para previsualización, pero no se envía como documento a `newIdentity`.

El paquete PROD incluido tiene los logs HTTP internos deshabilitados (`logEnabled = NO`). La aplicación integradora debe registrar únicamente la información necesaria desde los callbacks, evitando imprimir credenciales, imágenes o información sensible en producción.

---

## Localización

Descargue el archivo `MBLocalizable.strings`, modifique los textos requeridos y establezca el nombre del archivo en `customLocalizationFileName`.

---

## Requisitos

* **iOS 15.6 o superior**
* Xcode con soporte para integrar XCFrameworks y dependencias mediante Swift Package Manager.

### Requisitos adicionales

1. Agregar los archivos de licencia:

   * **com.become.document.key.txt**

2. Incluir el archivo de licencia en los recursos del target de la aplicación.

3. Verificar que el [`Bundle Identifier`](https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids) coincida con la licencia asignada al cliente.

---

## ¡Listo!

El SDK está listo para utilizarse en la integración de Become Digital.
