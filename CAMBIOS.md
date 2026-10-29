# Revisión al actualizar la integración

Estos son los aspectos de funcionamiento público que debes revisar al incorporar esta entrega de la SDK.

| Aspecto | Comportamiento y acción de integración |
| --- | --- |
| Inicialización | Utiliza `BDIVConfig(jwt:contractId:documenTypes:userId:)` con un JWT vigente obtenido por tu aplicación. La firma con `clienId` y `clientSecret` sigue disponible y está marcada como deprecada. |
| Consulta del resultado | Permite asignar `verificationResultsJwt` para usar un JWT de consulta diferente al de creación. Consulta la [guía de autenticación](AUTENTICACION.md). |
| Compatibilidad de integración | El paquete incluye iPhone físico y simuladores en Mac con Apple Silicon o Intel. Las capturas de cámara y rostro se comprueban en un dispositivo físico. |
| Flujos | Se mantienen **Onboarding** y **Authentication**. Para autenticar a un usuario existente, selecciona `flow: .Authentication` e indica su `userId`. |
| Pasos y documentos | Se muestran los pasos y tipos de documento disponibles para el contrato. Un único tipo también se presenta para confirmación. |
| Apariencia y textos | Se utilizan los asociados al contrato. El modo claro, oscuro o del sistema se elige con `themeMode`. |
| Datos iniciales | Puedes precargar país, estado, número de documento y subtipo mediante las opciones públicas de configuración. |
| Resultado | Utiliza los objetos opcionales `BDIVOnboardingResult`, `BDIVVerificationResult` y `BDIVAuthenticationResult`, según la operación. Reemplaza las lecturas de diccionarios de respuesta por sus propiedades. |
| Creación y confirmación | Con `performVerificationCheck=false` recibes la creación del registro. Con `true`, la SDK espera la confirmación. Crear un registro no implica su aprobación final. |
| Autenticación | Consulta `authentication.result` además del estado de la operación. |
| Captura facial | Un contrato que solo solicita documentos no exige resultado facial. |
| Capturas de pantalla | `preventScreenCapture` tiene valor predeterminado `false`. Actívalo explícitamente si necesitas la protección. |
| Diagnóstico | `debugLogsEnabled` permanece desactivado de forma predeterminada. Actívalo cuando necesites revisar una incidencia. |
| Localización | Agrega únicamente las claves que deseas personalizar, según la guía de localización de esta entrega. Los textos no personalizados conservan sus valores disponibles. |

Comprueba la instalación, licencia, permisos y manejo de resultados en un dispositivo físico antes de publicar la actualización de tu aplicación.
