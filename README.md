# Documentación de Become iOS SDK

Proceso de instalación de la librería become_IOS_SDK.

## Agregar Alamofire al proyecto
Se debe agregar la librería **Alamofire** al proyecto, click [aqui](https://github.com/Alamofire/Alamofire) para la documentación. 

## Agregar Blinkid al proyecto

 1. Se debe agregar la librería **Microblink.xcframework** al proyecto. 

 2. agregar archivo de texto **com.become.key.txt** con licencia

 <p align="center">
  <img src="https://github.com/Becomedigital/become_IOS_SDK/blob/master/IMG_4.png">
 </p>
 
  3. El [`Bundle Identifier`](https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids) del proyecto debe coincidir con la licencia asignada al cliente 

## Agregar Frameowrk al proyecto
Se debe agregar el archivo **BecomeDigitalV.framework**  en  las configuraciones generales del proyecto en la sección **framework, libraries, and embedded content**:

<p align="center">
  <img src="https://github.com/Becomedigital/become_IOS_SDK/blob/master/IMG_1.png">
</p>
 
Para el correcto funcionamiento de la SDK, se requiere el uso de los frameworks o librerías `CaptureUX.xcframework, CaptureCore.xcframework`; los cuales se deben adicionar en la sección **framework, libraries, and embedded content**:
 
 <p align="center">
  <img src="https://github.com/Becomedigital/become_IOS_SDK_ADC/blob/main/IMG_2.png">
</p>

## Configuraciones dentro de info.plist 

La SDK requiere que dentro de las configuraciones **info.plis**, se encuentre una descripción de uso de la cámara:

    Privacy - Camera Usage Description ( Esta aplicación hace uso de tu cámara)
    
 <p align="center">
  <img src="https://github.com/Becomedigital/become_IOS_SDK/blob/master/IMG_3.png">
 </p>
 
## Inicialización de la SDK

**1. Importar el SDK en nuestro viewController:**

        import  BecomeDigitalV


**2. En el método **startSDKAction ()** de su **viewController** de aplicación, inicialice Become utilizando el siguiente fragmento de código:**
 
         @IBAction func startSDKAction(_ sender: Any) {
            // Se crea un formateador de fechas para generar un identificador único basado en la fecha y hora actual
            let dateFormatter = DateFormatter()
            dateFormatter.locale = Locale(identifier: "es_ES") // Configuración regional para la identificación de la fecha del usuario
            dateFormatter.dateFormat = "yyyyMMddHHmmssSSS"
            let userId = dateFormatter.string(from: Date()) // Se obtiene un identificador único

            // Se configuran los parámetros necesarios para inicializar el objeto BDIVConfig
            let bdivConfig = BDIVConfig(clienId: "TU_CLIENT_ID",
                                        clientSecret: "TU_CLIENT_SECRET",
                                        contractId: "TU_CONTRACT_ID",
                                        useFacialAuth: true, // Indica si se debe utilizar la autenticación facial
                                        documenTypes: [.PASSPORT, .DNI, .DRIVERLICENSE], // Tipos de documentos permitidos
                                        userId: userId, // Identificador único del usuario
                                        customerLogo: "", // Ruta al logo personalizado (opcional)
                                        customLocalizationFileName: "MBLocalizable") // Nombre de el archivo con la localización 

            // Se establece el delegado para manejar las devoluciones de llamada del SDK
            BDIVCallBack.sharedInstance.delegate = self

            // Se registra la configuración del SDK con los parámetros especificados
            BDIVCallBack.sharedInstance.register(bdivConfig: bdivConfig)
        }


        extension ViewController: BDIVDelegate{
             func BDIVResponseSuccess(bdivResult: AnyObject) {
                 let idmResultFinal = bdivResult as! ResponseIV
                 print(String(describing: idmResultFinal))

             }

             func BDIVResponseError(error: String) {
                 print(error)
             }
        }

## Respuesta de la SDK 
**1. Estructura encargada de la definición del estado de validación exitoso:**

La SDK dará respuesta mediante dos métodos o promesas de respuesta, que pertenecen al estructura  **BDIVDelegate**:

      func BDIVResponseSuccess(bdivResult: AnyObject) {       
        let idmResultFinal = bdivResult as! ResponseIV        
        print(String(describing: idmResultFinal))           
      }        

      func BDIVResponseError(error: String) { 
        print(error)   
      }

## Estructura para el retorno de la información

Los siguientes parámetros permiten el retorno de la información capturada por el sistema mediante la promesa de respuesta o evento **BDIVResponseSuccess**:

      func BDIVResponseSuccess(bdivResult: AnyObject) {       
         let idmResultFinal = bdivResult as! ResponseIV        
         print(String(describing: idmResultFinal))           
      }        

## Estructura para el retorno de la información
Los siguientes parámetros permiten el retorno de la información capturada por el sistema:

    public var message: String = ""
    public var responseURL: String = ""
    public var responseStatus: typeEstatus = .PENDING


    typeEstatus {        
      case SUCCES        
      case ERROR        
      case PENDING    
    }

## Posibles Errores
**1. Error con parámetros vacíos**
Los siguientes parámetros son necesarios para la activación de la SDK por lo tanto su valor no debe ser vacío.

Parámetro | Valor
------------ | -------------
validationTypes | ""
clientSecret | ""
clientID | ""
contractID | ""
userID  | ""

Mostrará el siguiente error por consola:

    parameters cannot be empty

**2. Video cómo único parámetro**

El atributo **validationTypes** no puede contener como único valor el parámetro **VIDEO**.

    validationTypes: “VIDEO"

Mostrará el siguiente error por consola:

    the process cannot be initialized with video only

## Implementación del proceso

Esta sección se encarga de proporcionar el fragmento de código para la implementación final del proceso:

          import UIKit
          import  BecomeDigitalV

              class ViewController: UIViewController {

                  override func viewDidLoad() {
                      super.viewDidLoad()
                  }

                  @IBAction func startSDKAction(_ sender: Any) {
                      let dateFormatter = DateFormatter()
                      dateFormatter.locale = Locale(identifier: "es_ES") // date user identification
                      dateFormatter.dateFormat = "yyyyMMddHHmmssSSS"
                      let userId = dateFormatter.string(from: Date()) // Se inicializa un único identificador
                      let bdivConfig = BDIVConfig(clienId: "your_client_id", clientSecret: "your_client_secret", contractId: "your_contract_id", validationTypes:"VIDEO/PASSPORT/DNI/LICENSE", userId: , allowLibraryLoading: true, customerLogo: "")        BDIVCallBack.sharedInstance.delegate = self
                      BDIVCallBack.sharedInstance.register(bdivConfig: bdivConfig)


                  }
              }


              extension ViewController: BDIVDelegate{
                  func BDIVResponseSuccess(bdivResult: AnyObject) {
                      let idmResultFinal = bdivResult as! ResponseIV
                      print(String(describing: idmResultFinal))

                  }

                  func BDIVResponseError(error: String) {
                      print(error)
                  }
              }
              
## Localización

Descargue el archivo `MBLocalizable.strings` de ejemplo y modifique el texto que requiera, luego agregue el nombre del archivo en el parámetro `customLocalizationFileName`.

## Requerimientos
•	Tecnologías
iOS 12 en adelante
•	Alamofire
5.5.0 / Swift Package Manager