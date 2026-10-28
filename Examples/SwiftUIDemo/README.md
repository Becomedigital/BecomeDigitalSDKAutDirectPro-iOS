# Ejemplo de integración con SwiftUI

Este proyecto muestra cómo iniciar la SDK de iOS distribuida desde SwiftUI. `BecomeSwiftUIScreen` presenta `BecomeSDKBridge`, que conserva un controlador de UIKit mientras la verificación está activa y recibe las respuestas de `BDIVDelegate`. La aplicación también atiende los eventos de sesiones en segundo plano e incluye recursos en inglés, español y español latinoamericano para su pantalla y los componentes nativos compatibles.

El repositorio no incluye credenciales de cliente ni licencia de captura para este ejemplo. Para completar una verificación necesitas un contrato con Become, las credenciales de ese contrato y una licencia emitida para el identificador de tu aplicación. Sin estos datos, el ejemplo compila, pero muestra un aviso de configuración faltante cuando intentas iniciar la SDK.

## Preparar la aplicación local

1. Lee la [guía de instalación](../../INSTALACION.md). Utiliza Xcode 27 o posterior e iOS 16 o posterior.
2. Copia `App/Secrets.example.plist` como `App/Secrets.plist` y escribe los valores `clientId`, `clientSecret` y `contractId` entregados para tu integración. El archivo real está excluido de Git.
3. Coloca la licencia de captura emitida para tu aplicación en `App/com.become.document.key.txt`. Este archivo también está excluido de Git. La licencia debe ser válida para el identificador y el ambiente que vas a probar.
4. Indica el identificador autorizado de tu aplicación y vuelve a generar el proyecto:

   ```bash
   BECOME_DEMO_BUNDLE_ID=com.suempresa.suapp ruby generate_project.rb
   ```

   El generador requiere la gema de Ruby `xcodeproj`. Agrega los dos archivos privados a los recursos de la aplicación solo cuando existen. Vuelve a generar el proyecto después de agregar o quitar cualquiera de ellos.
5. Abre `BecomeSwiftUIDemo.xcodeproj`, selecciona tu equipo de firma y compila para un iPhone físico. Ingresa un identificador de usuario y toca **Iniciar verificación**.

La aplicación utiliza directamente `BDIdentityVerification.xcframework` de este repositorio; el ejemplo no contiene una segunda copia. El proyecto fija las versiones de los paquetes Swift indicadas en la [guía de instalación](../../INSTALACION.md). Si modificas el proyecto generado, revisa los recursos incluidos antes de compartirlo. No agregues a Git `Secrets.plist`, la licencia ni una aplicación compilada.

`BDIVConfig.debugLogsEnabled` está activado para generar mensajes de diagnóstico. Los registros de una prueba pueden contener información personal. La [guía de localización](../../LOCALIZACION.md) distingue los textos entregados por el contrato de los textos nativos que puede traducir la aplicación. Consulta también la [guía de registros](../../LOGGING.md).

La captura de documentos y la validación facial requieren un dispositivo físico y datos válidos de integración. Una compilación correcta para simulador solo confirma que el código y los recursos se empaquetan.
