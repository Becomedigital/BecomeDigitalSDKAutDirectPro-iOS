# Ejemplo de integración con SwiftUI Legacy

Esta aplicación muestra cómo iniciar la SDK distribuida desde SwiftUI y recibir el resultado o la cancelación mediante `BDIVDelegate`. Incluye el manejo de las transferencias en segundo plano y recursos de localización en español, español de Latinoamérica e inglés.

## Preparar la aplicación

1. Consulta los requisitos y dependencias de la [guía de instalación](../../README.md#installation-and-dependencies). Utiliza Xcode 27 o posterior e iOS 16 o posterior.
2. Copia `App/Secrets.example.plist` como `App/Secrets.plist` y completa `clientId`, `clientSecret` y `contractId` con los valores de tu integración. El archivo local está excluido de Git.
3. Agrega la licencia emitida para tu aplicación como `App/com.become.document.key.txt`. Utiliza una licencia válida para el identificador y ambiente de tu aplicación. Este archivo también está excluido de Git.
4. Configura el identificador autorizado de tu aplicación. Si agregaste las credenciales o la licencia, utiliza `generate_project.rb` para incluir esos archivos en el proyecto; requiere la gema `xcodeproj`. La variable `BECOME_DEMO_BUNDLE_ID` permite indicar tu identificador al generarlo.
5. Abre **`BecomeSwiftUIDemoLegacy.xcworkspace`**, selecciona tu equipo de firma y genera la aplicación para un iPhone físico. Ingresa el identificador del usuario y toca **Start onboarding**.

El workspace conserva el proyecto `BecomeSwiftUIDemo.xcodeproj` y las dependencias de la [guía de instalación](../../README.md#installation-and-dependencies). Utiliza directamente el `BDIdentityVerification.xcframework` incluido en el repositorio. El generador conserva el nombre del workspace con el sufijo `Legacy`.

El ejemplo puede compilar sin credenciales ni licencia; para completar una verificación requiere los valores válidos de tu integración. Si faltan, muestra un mensaje al intentar iniciar. No compartas las credenciales, la licencia ni una aplicación que las incluya.

## Idioma y diagnóstico

El ejemplo activa `BDIVConfig.debugLogsEnabled` para facilitar el soporte. Consulta la [guía de diagnóstico](../../LOGGING.md) y desactiva la opción cuando termines las pruebas. La [guía de localización](../../LOCALIZACION.md) describe los textos y claves admitidos para personalizar tu aplicación.

La captura de documentos y la validación facial requieren un dispositivo físico y una licencia válida para tu aplicación.
