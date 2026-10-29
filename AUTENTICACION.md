# Inicialización con JWT y migración de la firma anterior — iOS

Esta entrega recomienda la inicialización con `jwt`. La firma con `clienId` y `clientSecret` se conserva para las integraciones existentes y está marcada como **deprecada**. No se anuncia una fecha de retiro de esa firma.

## Preparar los tokens desde tu backend

Antes de iniciar una verificación, obtén los JWT desde el backend de tu aplicación. Entrega únicamente sus valores, **sin el prefijo `Bearer`**, para el mismo ambiente y contrato de tu integración. Mantén las credenciales de cliente en tu backend.

Para onboarding con consulta del resultado final, prepara dos tokens:

| Operación de la integración | Permiso solicitado | Configuración pública |
| --- | --- | --- |
| Crear la verificación | `verification:create` | Argumento `jwt` del inicializador. |
| Consultar el resultado | `verification:get` | Propiedad `verificationResultsJwt`, asignada antes de iniciar la SDK. |

Consulta la [guía de autenticación](https://becomedigital.gitbook.io/kyc_api_es/authentication), la [obtención de tokens](https://becomedigital.gitbook.io/kyc_api_es/endpoints/auth) y los [permisos para consultar resultados](https://becomedigital.gitbook.io/kyc_api_es/endpoints/verification-results). Cada token debe estar autorizado para la operación correspondiente. Cambiar únicamente el permiso del token principal a `verification:get` deja sin cubrir la creación.

## Firma recomendada

```swift
// Ambos tokens se reciben desde el backend de la aplicación.
var config = BDIVConfig(
    jwt: creationJwt,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId,
    flow: .Onboarding,
    themeMode: .system
)
config.verificationResultsJwt = resultsJwt
let verification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
verification.startVerification()
```

Conserva la instancia de `BecomeDigitalSDK` mientras la verificación esté activa y atiende `BDIVDelegate` como se muestra en el [README](README.md).

`verificationResultsJwt` solo se utiliza al consultar el resultado de onboarding con `performVerificationCheck: true`, que es el valor predeterminado. No reemplaza `jwt` para crear la verificación ni selecciona el flujo `Authentication`. Con `performVerificationCheck: false`, se recibe la creación sin esperar su resultado final. En `flow: .Authentication`, el token principal debe autorizar ese flujo; esta propiedad no cambia su comportamiento.

Por compatibilidad, el valor predeterminado de `verificationResultsJwt` es `nil`: si no lo asignas, se conserva el uso del token principal para la consulta. Esto solo funciona si ese token tiene el permiso necesario; un token limitado a `verification:create` no autoriza la consulta de resultados. Un valor explícito vacío o compuesto por espacios se rechaza al intentar consultar, sin utilizar otro token como reemplazo.

La SDK no obtiene ni renueva los tokens de la firma JWT y no cambia automáticamente a la firma con credenciales. Si un token vence o es rechazado, obtén los tokens vigentes desde tu backend y crea una nueva configuración y otra instancia antes de un nuevo intento. No muestres ni registres los JWT.

## Si se crea la verificación, pero la consulta devuelve HTTP 403

Una creación confirmada con HTTP 201 seguida de HTTP 403 al consultar puede indicar que el JWT de consulta no tiene el permiso requerido. No significa por sí sola que el token haya vencido.

Revisa que `jwt` corresponda a creación (`verification:create`) y que hayas asignado un token autorizado para consulta (`verification:get`) a `verificationResultsJwt` antes de iniciar la SDK. Comprueba también vigencia, ambiente, contrato y permisos de tu integración. Si el problema continúa, comparte con soporte el estado HTTP y el paso afectado, sin incluir tokens, credenciales ni datos personales.

Los avisos de UIKit o WebKit no explican por sí solos este rechazo HTTP. Consulta también el [manejo de errores](ERRORES.md).

## Firma anterior, deprecada y compatible

```swift
// Firma deprecada; se conserva para las integraciones existentes.
let config = BDIVConfig(
    clienId: clientId,
    clientSecret: clientSecret,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId
)
```

Xcode muestra la advertencia de deprecación en el inicializador con credenciales y en las propiedades `clienId` y `clientSecret`, e identifica la firma con `jwt` como reemplazo. Conserva la escritura original de `clienId` mientras uses la firma anterior.

Las aplicaciones existentes mantienen su forma de iniciar la verificación y sus opciones de flujo, documentos, apariencia, diagnóstico y consulta. La firma deprecada conserva la obtención del token; `verificationResultsJwt` no modifica esa ruta. No asignes esta propiedad para cambiar la autenticación de una configuración creada con credenciales.

## Migrar una integración

1. Reemplaza el archivo de la SDK y conserva las dependencias de la [guía de instalación](INSTALACION.md).
2. Prepara en tu backend los tokens para las operaciones que utiliza tu app.
3. Sustituye `clienId` y `clientSecret` por `jwt` al crear `BDIVConfig`.
4. Para onboarding con consulta final, declara la configuración con `var` y asigna `verificationResultsJwt` antes de crear `BecomeDigitalSDK`.
5. Conserva `contractId`, documentos, usuario, parámetros opcionales y el manejo de resultados, errores y cancelación. Comprueba la nueva integración en un dispositivo físico antes de publicarla.
