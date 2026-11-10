# Migrar la integración Legacy de iOS a SPM

La versión oficial `3.5.1` permite agregar Become mediante una versión exacta. Conserva los JWT, el contrato, la licencia de tu aplicación, los permisos y las traducciones que utilizas.

## Retirar la integración por archivo

1. Identifica el target que inicia la verificación.
2. Retira la referencia local de `BDIdentityVerification.xcframework` y sus entradas de **Link Binary With Libraries**, **Embed Frameworks** y **Frameworks, Libraries, and Embedded Content**.
3. Retira los productos, copias locales y rutas de búsqueda que agregaste exclusivamente para las dependencias de esa integración. Conserva los paquetes que tu propia app utilice directamente; sus versiones deben ser compatibles con los requisitos del paquete de Become.
4. Conserva `com.become.document.key.txt`, las descripciones de permisos y los recursos de localización.

## Agregar la versión exacta

En Xcode, abre **File > Add Package Dependencies**, agrega `https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro-iOS.git`, selecciona **Exact Version** con `3.5.1` y asocia el producto `BDIdentityVerification` al target de tu app. SPM descarga el XCFramework y resuelve sus dependencias.

El módulo importado sigue siendo `BDIdentityVerification`. Sigue la [instalación](INSTALACION.md) y conserva la [inicialización y los callbacks](README.md#iniciar-una-verificación) de tu integración.

## Comprobar la integración

Confirma la versión en **Package Dependencies** y compila para los destinos que utiliza tu aplicación. En un dispositivo físico, prueba la licencia, los permisos, la captura de documentos, la validación facial, la cancelación y los resultados antes de distribuir tu app.
