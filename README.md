# Documentación del SDK de Become iOS

### Agregar la Licencia al Proyecto

1. Agregue un archivo de texto llamado **com.become.key.txt** que contenga la clave de licencia proporcionada.

   <p align="center">
   <img src="https://github.com/Becomedigital/become_IOS_SDK/blob/master/IMG_4.png">
   </p>

2. Asegúrese de que el [`Bundle Identifier`](https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids) del proyecto coincida con la licencia asignada al cliente.

## Agregar el Framework al Proyecto

Para integrar el SDK en su proyecto, siga estos pasos:

1. Agregue el archivo **BecomeDigitalV.xcframework** a la sección **Frameworks, Libraries, and Embedded Content** en la configuración de su proyecto en Xcode.
2. El SDK requiere los siguientes frameworks para su correcto funcionamiento:
   - `CaptureUX.xcframework`
   - `CaptureCore.xcframework`
   
   Estos deben añadirse también en la sección **Frameworks, Libraries, and Embedded Content**.

   <p align="center">
   <img src="https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro/blob/main/IMG_2.png">
   </p>

### Integración con Swift Package Manager

1. Abra su proyecto en Xcode y vaya a **File > Add Packages**.
   
   ![Agregar dependencia del paquete](https://github.com/user-attachments/assets/f845c6f2-d235-43a8-a1e3-a796cc1426a4))

2. En la barra de búsqueda, ingrese la URL del repositorio de la biblioteca Amplify:  
   `https://github.com/aws-amplify/amplify-swift`

3. Seleccione la opción **Up to Next Major Version** y especifique **2.0.0** como versión mínima. Luego, haga clic en **Add Package**.

   ![Opciones de versión de dependencia](https://github.com/aws-amplify/amplify-swift/blob/main/readme-images/spm-setup-02-amplify-repo-options.png)

4. Seleccione las bibliotecas necesarias según sus requerimientos:
   - **Amplify** (Obligatorio)
   
   ![Seleccionar dependencias](https://github.com/aws-amplify/amplify-swift/blob/main/readme-images/spm-setup-03-select-dependencies.png)

5. Repita los pasos anteriores para agregar el siguiente paquete:
   - `https://github.com/aws-amplify/amplify-ui-swift-liveness`

## Configuración en el Info.plist

El SDK requiere permisos de acceso a la cámara. Agregue la siguiente clave en su `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Requerimos acceso a la cámara para propósitos de verificación de identidad.</string>
```

## Inicialización del SDK

### Importar el SDK

```swift
import BecomeDigitalV
```

### Inicializar e Iniciar el Proceso de Verificación

```swift
let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                            clientSecret: "TU_CLIENT_SECRET",
                            contractId: "TU_CONTRACT_ID",
                            useFacialAuth: true,
                            documenTypes: [.DNI, .DRIVERLICENSE, .PASSPORT],
                            userId: "TU_USER_ID",
                            customerLogo: "icon",
                            customLocalizationFileName: "")

let identityVerification = BDIdentityVerification(bdivConfig: bdivConfig, delegate: self)
identityVerification.startVerification()
```

## Manejo de Respuestas del SDK

El SDK proporciona respuestas a través de los métodos de `BDIVDelegate`, retornando un objeto `ResponseIV`:

```swift
func BDIVResponseSuccess(bdivResult: AnyObject) {
    let idmResultFinal = bdivResult as! ResponseIV
    print(String(describing: idmResultFinal))
}

func BDIVResponseError(error: String) {
    print(error)
}
```

### Estructura ResponseIV

```swift
public struct ResponseIV {
    public var message: String = ""
    public var responseURL: String = ""
    public var responseStatus: StatusType = .PENDING

    public enum StatusType {
        case SUCCESS
        case ERROR
        case PENDING
        case NOFOUND
    }
}
```

## Errores Comunes

### 1. Parámetros Requeridos Vacíos

Los siguientes parámetros no deben estar vacíos para la activación del SDK:

| Parámetro       | Valor |
|----------------|-------|
| validationTypes | ""    |
| clientSecret   | ""    |
| clientID       | ""    |
| contractID     | ""    |
| userID         | ""    |

Error en consola:

```text
parameters cannot be empty
```

### 2. Tipo de Validación Inválido

El atributo `validationTypes` no puede contener únicamente `VIDEO`.

```swift
validationTypes: "VIDEO"
```

Error en consola:

```text
the process cannot be initialized with video only
```

## Ejemplo de Implementación

```swift
import UIKit
import BecomeDigitalV

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
    }

    @IBAction func startSDKAction(_ sender: Any) {
        let dateFormatter = DateFormatter()
        dateFormatter.locale = Locale(identifier: "es_ES")
        dateFormatter.dateFormat = "yyyyMMddHHmmssSSS"
        let userId = dateFormatter.string(from: Date())

        let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                                    clientSecret: "TU_CLIENT_SECRET",
                                    contractId: "TU_CONTRACT_ID",
                                    useFacialAuth: true,
                                    documenTypes: [.DNI, .DRIVERLICENSE, .PASSPORT],
                                    userId: userId,
                                    customerLogo: "icon",
                                    customLocalizationFileName: "")

        let identityVerification = BDIdentityVerification(bdivConfig: bdivConfig, delegate: self)
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

## Localización

Descargue el archivo `MBLocalizable.strings`, modifique el texto requerido y establezca el nombre del archivo en `customLocalizationFileName`.

## Requisitos

- **iOS 12. o superior**
=======
1. Agregar archivos de licencia:

   - **com.become.document.key.txt**: Llaves de inicialización para la captura de documentos.
   - **com.become.finger.lic**: Llaves de inicialización para la captura de huellas.

Estos archivos deben estar incluidos en los recursos del proyecto.

2. El [`Bundle Identifier`](https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids) del proyecto debe coincidir con la licencia asignada al cliente.

---

## Agregar Framework al proyecto

Se debe agregar el archivo **BecomeDigitalV.xcframework** en las configuraciones generales del proyecto en la sección **Frameworks, Libraries, and Embedded Content**.

Además, para el correcto funcionamiento de la SDK, se requiere el uso de los siguientes frameworks/librerías:

- `CaptureUX.xcframework`
- `CaptureCore.xcframework`

Estos deben adicionarse en la sección mencionada.

<p align="center">
<img src="https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro/blob/main/IMG_2.png">
</p>

### Instalación mediante CocoaPods

Agregar el siguiente contenido en su `Podfile`:

```ruby
platform :ios, '15.6'

plugin 'cocoapods-art', :sources => [
  'cocoapods-identy-finger'
]

target 'BecomeApp' do
  use_frameworks!

  pod 'Identy', '6.3.0'
end
```

**Instalación de cocoapods-art:**

```bash
sudo gem install cocoapods-art
```

**Nota:** Las credenciales para acceder al repositorio privado serán proporcionadas directamente por Become.

### Integración con Swift Package Manager

Es necesario agregar los siguientes paquetes para completar la configuración de la SDK:

1. Abra su proyecto en Xcode y vaya a **File > Add Packages**.

   ![Agregar dependencia del paquete](https://github.com/user-attachments/assets/f845c6f2-d235-43a8-a1e3-a796cc1426a4)

2. En la barra de búsqueda, ingrese la URL del repositorio de la biblioteca Amplify:  
   `https://github.com/aws-amplify/amplify-swift`

3. Seleccione la opción **Up to Next Major Version** y especifique **2.0.0** como versión mínima. Luego, haga clic en **Add Package**.

   ![Opciones de versión de dependencia](https://github.com/aws-amplify/amplify-swift/blob/main/readme-images/spm-setup-02-amplify-repo-options.png)

4. Seleccione las bibliotecas necesarias según sus requerimientos:
   - **Amplify** (Obligatorio)

   ![Seleccionar dependencias](https://github.com/aws-amplify/amplify-swift/blob/main/readme-images/spm-setup-03-select-dependencies.png)

5. Repita los pasos anteriores para agregar el siguiente paquete:
   - `https://github.com/aws-amplify/amplify-ui-swift-liveness`

---

## Configuraciones dentro de info.plist

Debe agregarse la descripción de uso de la cámara y del reconocimiento de voz:

```xml
<key>NSCameraUsageDescription</key>
<string>Esta aplicación hace uso de tu cámara</string>

<key>NSSpeechRecognitionUsageDescription</key>
<string>Esta aplicación necesita acceso al reconocimiento de voz para procesar comandos o analizar el audio del usuario.</string>
```

---

## Inicialización de la SDK

**1. Importar el SDK en su ViewController:**

```swift
import BDIdentityVerification
```

**2. Inicializar Become SDK:**

> ⚠️ **Nota importante:** Recuerde reemplazar los valores `<TU_CLIENT_ID>`, `<TU_CLIENT_SECRET>` y `<TU_CONTRACT_ID>` por los datos reales proporcionados para su integración.

```swift
@IBAction func startSDKAction(_ sender: Any) {

    let bdivConfig = BDIVConfig(
        clienId: "<TU_CLIENT_ID>",
        clientSecret: "<TU_CLIENT_SECRET>",
        contractId: "<TU_CONTRACT_ID>",
        documenTypes: [.DNI],
        userId: "<TU_USER_ID>",
        customerLogo: "becomeIcon",
        customLocalizationFileName: "Localizable"
    )

    let identityVerification = BecomeDigitalSDK(bdivConfig: bdivConfig, delegate: self)
    identityVerification.startVerification()
}
```

**Importante:**
- El parámetro `customLocalizationFileName` debe apuntar a un archivo **Localizable.strings** donde se encuentran todas las llaves de los textos a localizar.

**3. Delegado de la SDK:**

```swift
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

## Respuesta de la SDK

La SDK proporcionará respuestas a través de los métodos del protocolo **BDIVDelegate**:

```swift
func BDIVResponseSuccess(bdivResult: AnyObject) {
    let idmResultFinal = bdivResult as! ResponseIV
    print(String(describing: idmResultFinal))
}

func BDIVResponseError(error: String) {
    print(error)
}
```

Los parámetros disponibles en el objeto de respuesta incluyen:

```swift
public var message: String = ""
public var responseURL: String = ""
public var responseStatus: typeEstatus = .PENDING

enum typeEstatus {        
  case SUCCES
  case ERROR
  case PENDING
}
```

---

## Posibles Errores

**Error por parámetros vacíos**

Es necesario que los siguientes parámetros tengan valor:

Parámetro | Valor
------------ | -------------
clientSecret | ""
clientID | ""
documenTypes | ""
contractID | ""
userID  | ""

Error mostrado:

```bash
parameters cannot be empty
```

---

## Localización

Descargue o cree el archivo `Localizable.strings` donde agregará los textos personalizados que usará la SDK. Este archivo se indica en el parámetro `customLocalizationFileName`.

---

## Requerimientos

- iOS 12 o superior

---

# ¡Listo!

Su SDK está lista para ser utilizada con la integración Become Digital.
>>>>>>> release_finger
