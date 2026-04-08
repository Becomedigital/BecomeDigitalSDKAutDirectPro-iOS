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

## Versiones requeridas

Configure las dependencias con las siguientes versiones:

* **Amplify Swift**: `2.45.4`
* **Amplify UI Swift Liveness**: `1.3.4`
* **BlinkID Capture Core**: rama `main`
* **BlinkID Capture UX**: rama `main`

---

## Agregar licencias al proyecto

Agregue los archivos de licencia proporcionados para la inicialización del SDK y la captura de documentos.

### Archivos requeridos

* **com.become.document.key.txt**

Estos archivos deben estar incluidos en los recursos del proyecto y en el target correspondiente.

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

Utilice la siguiente configuración:

* **amplify-swift** → `Up to Next Major Version` desde `2.45.4`
* **amplify-ui-swift-liveness** → `Up to Next Major Version` desde `1.3.4`
* **capture-core-sp** → `Branch: main`
* **capture-ux-sp** → `Branch: main`

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
import BecomeDigitalV
```

### Inicializar e iniciar el proceso de verificación

```swift
let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                            clientSecret: "TU_CLIENT_SECRET",
                            contractId: "TU_CONTRACT_ID",                            
                            documenTypes: [.DNI, .DRIVERLICENSE, .PASSPORT],
                            userId: "TU_USER_ID",
                            customerLogo: "icon",
                            customLocalizationFileName: "")

let identityVerification = BDIdentityVerification(bdivConfig: bdivConfig, delegate: self)
identityVerification.startVerification()
```

---

## Manejo de respuestas del SDK

El SDK responde a través de los métodos del protocolo `BDIVDelegate`, retornando un objeto `ResponseIV`.

```swift
func BDIVResponseSuccess(bdivResult: AnyObject) {
    let idmResultFinal = bdivResult as! ResponseIV
    print(String(describing: idmResultFinal))
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
    
    /// Initializes a new instance of `ResponseIV` with provided values.
///
/// - Parameters:
///   - message: A textual description of the result.
///   - responseDictionary: A dictionary containing additional data returned from the verification process.
///   - responseStatus: The current verification status represented by a `StatusType` value.
    internal init(message: String = "", responseDictionary: [String : Any] = [:], responseStatus: BDIdentityVerificationResponse.StatusType = .PENDING) {
        self.message = message
        self.responseDictionary = responseDictionary
        self.responseStatus = responseStatus
    }
    
    /// Default initializer for `ResponseIV`.
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
            print("Failed to convert ResponseIV to JSON: \(error)")
            return nil
        }
    }
}
```

---

## Errores comunes

### 1. Parámetros requeridos vacíos

Los siguientes parámetros no deben enviarse vacíos:

| Parámetro         | Valor inválido |
| ----------------- | -------------- |
| `clientSecret`    | `""`           |
| `clientID`        | `""`           |
| `contractID`      | `""`           |
| `userID`          | `""`           |

Error en consola:

```text
parameters cannot be empty
```

### 2. Flujo facial no disponible

Si el flujo facial no inicia correctamente, valide que:

* `amplify-swift` esté agregado
* `amplify-ui-swift-liveness` esté agregado
* Las versiones configuradas coincidan con las requeridas
* Las dependencias de Microblink estén incluidas en el target

---

## Ejemplo de implementación

```swift
import UIKit
import BecomeDigitalV

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
    }

    @IBAction func startAction(_ sender: Any) {
        let dateFormatter = DateFormatter()
        dateFormatter.locale = Locale(identifier: "es_ES") 
        dateFormatter.dateFormat = "yyyyMMddHHmmssSSS"
        let userId = dateFormatter.string(from: Date())???

        let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                                    clientSecret: "TU_CLIENT_SECRET",
                                    contractId: "TU_CONTRACT_ID",
                                    documenTypes: [.DNI, .DRIVERLICENSE, .PASSPORT],
                                    userId: userId,
                                    customerLogo: "icon",
                                    customLocalizationFileName: "")

        let identityVerification = BecomeDigitalSDK(bdivConfig: bdivConfig, delegate: self)
        identityVerification.startVerification()
    }
}

extension ViewController: BDIVDelegate {
    func BDIVResponseSuccess(bdivResult: AnyObject) {
        let idmResultFinal = bdivResult as! ResponseIV
        print(String(describing: idmResultFinal))
    }

    func BDIVResponseError(error: String) {
        print(error)
    }
}
```

---

## Localización

Descargue el archivo `MBLocalizable.strings`, modifique los textos requeridos y establezca el nombre del archivo en `customLocalizationFileName`.

---

## Requisitos

* **iOS 15.6 o superior**

### Requisitos adicionales

1. Agregar los archivos de licencia:

   * **com.become.document.key.txt**

2. Incluir ambos archivos en los recursos del proyecto.

3. Verificar que el [`Bundle Identifier`](https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids) coincida con la licencia asignada al cliente.

---

## ¡Listo!

Su SDK está lista para ser utilizada con la integración de Become Digital.
