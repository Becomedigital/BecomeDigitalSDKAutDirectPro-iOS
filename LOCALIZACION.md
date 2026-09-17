# Localización y personalización de textos en iOS

Esta guía corresponde al `BDIdentityVerification.xcframework` incluido en este repositorio: Become 1.2.3, CaptureUX 1.4.3 y Amplify UI Swift Liveness 1.4.4. La plantilla [Localizable.strings](Localizable.strings) contiene claves de varios componentes; **no todas permiten sobrescritura desde la aplicación cliente**.

## Qué textos puede personalizar la aplicación

| Componente | Claves | Origen y alcance |
| --- | --- | --- |
| Amplify Face Liveness | `amplify_ui_liveness_*` | Busca en `Localizable.strings` del bundle principal de la app. Si no encuentra la clave, usa su recurso interno. |
| Microblink CaptureUX | `mbic_*` | Busca en la tabla del bundle principal indicada por `customLocalizationFileName`. Las claves no definidas mantienen el texto de los recursos de Microblink. |
| Pantallas propias de Become | `text_*`, `error_*`, `unknown_error` y otras del bloque Become | Lee `Dictionary.stringsdict` del bundle de `BDIdentityVerification.framework`. **No busca estas claves en el archivo de la app.** |
| Claves históricas de Identy | `identy_*`, `id_*`, `search_*` y claves de storyboard | Se conservan por compatibilidad; no son el mecanismo de personalización de Microblink ni de Amplify y no habilitan funcionalidades adicionales. |

La sobrescritura de Face Liveness está documentada por [AWS Amplify](https://ui.docs.amplify.aws/swift/connected-components/liveness/customization#internationalization-i18n). Se verificó además la búsqueda `Bundle.main` con respaldo en `Bundle.module` del helper `String+Localizable.swift` de la versión 1.4.4.

Para Microblink se verificó `MBIC_UI_LOCALIZED` en `CaptureUX.framework/Headers/MBICCaptureUISDK.h` de la versión 1.4.3. Su propiedad `customLocalizationFileName` sigue disponible, pero está marcada como **deprecated** por Microblink. Es el mecanismo expuesto actualmente por `BDIVConfig`; debe revisarse al actualizar CaptureUX. Consulte la [localización de Capture iOS 1.4.3](https://github.com/BlinkID/capture-ios/tree/v1.4.3#localization).

## 1. Agregar los textos al target de la app

1. Descargue [Localizable.strings](Localizable.strings). Si su app ya tiene ese archivo, combine únicamente las claves que necesite; no reemplace sus textos ni agregue claves duplicadas.
2. Agréguelo a Xcode con **Add Files to…** y seleccione el target de la aplicación integradora en **Target Membership**. Debe quedar en el bundle principal de la app, no solamente en un framework o paquete auxiliar.
3. Compruebe su inclusión en **Build Phases → Copy Bundle Resources**. Para archivos localizados se mostrará el grupo de variantes.
4. Modifique los valores a la derecha de `=`; conserve las claves exactas. Puede incluir solo las claves compatibles que quiera sobrescribir.

Ejemplo para los textos en español:

```text
/* Face Liveness */
"amplify_ui_liveness_get_ready_begin_check" = "Iniciar verificación facial";
"amplify_ui_liveness_challenge_connecting" = "Conectando...";

/* Microblink */
"mbic_scan_the_front_side" = "Escanea el frente del documento";
"mbic_scan_the_back_side" = "Escanea el reverso del documento";
"mbic_onboarding_title" = "Coloca el teléfono en horizontal";
"mbic_onboarding_message" = "Mantén el teléfono en horizontal y verifica que todos los campos del documento sean visibles.";
```

La plantilla del repositorio es una base en inglés, no una traducción automática. Cambiar un texto no altera el flujo, las validaciones, los reintentos ni los resultados del servicio.

## 2. Configurar Microblink desde BDIVConfig

Use el nombre del archivo **sin extensión**, respetando mayúsculas y minúsculas:

```swift
import BDIdentityVerification

let config = BDIVConfig(
    clienId: "TU_CLIENT_ID",
    clientSecret: "TU_CLIENT_SECRET",
    contractId: "TU_CONTRACT_ID",
    documenTypes: [.DNI, .PASSPORT],
    userId: "TU_USER_ID",
    customLocalizationFileName: "Localizable"
)
```

Se conservan los nombres públicos `clienId` y `documenTypes` de la API. Use esta configuración al crear `BecomeDigitalSDK`, como muestra el [ejemplo de integración](README.md).

El valor predeterminado del parámetro sigue siendo `"MBLocalizable"`. Si agrega `Localizable.strings` pero omite el parámetro, Microblink buscará una tabla distinta. Amplify no utiliza ese parámetro: siempre consulta su tabla `Localizable`.

Si prefiere separar los textos, deje las claves `amplify_ui_liveness_*` en `Localizable.strings`, coloque las `mbic_*` en `MBLocalizable.strings` y configure `"MBLocalizable"`. No renombre todo el archivo a `MBLocalizable.strings`: Amplify dejaría de encontrar allí sus personalizaciones.

Establezca el nombre explícitamente en cada inicio. `nil` no configura una tabla nueva en esa inicialización y no garantiza limpiar una personalización previa del singleton de Microblink.

## 3. Varios idiomas

En **Project → Info → Localizations**, agregue los idiomas de la app. Seleccione el archivo y use **File Inspector → Localize…** para crear sus variantes. Traduzca los valores en cada variante, manteniendo las mismas claves:

```text
App/
  en.lproj/Localizable.strings
  es.lproj/Localizable.strings
  es-419.lproj/Localizable.strings   (opcional, español latinoamericano)
```

No mantenga además otra copia no localizada del mismo archivo en la raíz del bundle. La selección se basa en los idiomas soportados y las preferencias de la app; `customLocalizationFileName` selecciona una **tabla**, no un idioma. El framework Become distribuido incluye recursos `en`, `es` y `es-419`. Consulte [los recursos de cadenas de Apple](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/LoadingResources/Strings/Strings.html).

Si usa `Localizable.xcstrings` en su app, incorpore las claves en ese catálogo y evite producir dos tablas `Localizable` para el mismo idioma.

## 4. Limitaciones de los textos propios de Become

El método interno `String.localize(bundle:)` carga `Dictionary.stringsdict` desde el bundle de la clase del SDK. Por ejemplo, `text_title_button_retry` y `unknown_error` no se buscan en `Bundle.main`.

Las 103 claves del bloque **Become — SOLO REFERENCIA** permiten consultar el inventario completo del recurso distribuido. Agregarlas o traducirlas en el archivo de la app **no cambia las pantallas de Become en este binario**. También hay entradas técnicas, como `splitValidationTypes`, `validation_type_video` y `_07`, que no deben tratarse como textos de UI traducibles.

Para habilitar esa personalización se necesita un cambio del resolvedor de textos en el código fuente de Become y una nueva distribución del SDK. No modifique los recursos internos del XCFramework entregado: alteraría el paquete y sus firmas. Esta actualización de documentación no cambia ese comportamiento ni sustituye el binario.

Los mensajes enviados por el backend, los textos definidos directamente en código y los textos del sistema tampoco se sustituyen automáticamente con estas claves. Los mensajes de permisos de iOS, por ejemplo `NSCameraUsageDescription`, pertenecen a la configuración de la app y se localizan mediante `InfoPlist.strings`, no con `Localizable.strings`.

## 5. Reglas de edición

- Guarde como UTF-8 y use el formato `"clave" = "valor";`.
- Mantenga una sola definición por clave e idioma. No corrija nombres como `mbic_lightning_too_dark` o `text_varification_title`: son identificadores existentes.
- Conserve exactamente los parámetros de formato y sus tipos. En el inventario Become, `text_info_upload` y `text_info_upload_document` contienen `%d%%`; `liveness_detection_failed` y `error_low_confidence` contienen `%@`.
- Use `\n` para saltos de línea, `\"` para comillas dentro de un valor y `\\` para una barra invertida.
- No vacíe instrucciones esenciales ni advertencias de fotosensibilidad. Traduzca manteniendo su significado; AWS desaconseja modificar la pantalla de preparación y los parámetros del desafío por razones de éxito y seguridad. [Buenas prácticas de Face Liveness](https://ui.docs.amplify.aws/swift/connected-components/liveness/customization#best-practices).

## 6. Verificación de la integración

Valide la sintaxis de la plantilla y, en su proyecto, de cada traducción:

```sh
plutil -lint Localizable.strings
plutil -lint en.lproj/Localizable.strings es.lproj/Localizable.strings
```

1. En Xcode, seleccione **Edit Scheme → Run → Options → App Language** y pruebe cada idioma.
2. Cambie temporalmente una clave `mbic_*` y una `amplify_ui_liveness_*`; ejecute ambos pasos del flujo en un dispositivo y compruebe que aparecen sus valores.
3. Retire temporalmente una de esas claves y verifique el respaldo del componente. Una clave con valor vacío no equivale a omitirla.
4. Compruebe textos largos, accesibilidad y orientación. Si no cambia un texto, revise el target, la tabla configurada, la variante de idioma y a qué componente pertenece.
5. Recompile la app después de editar sus recursos. No es necesario regenerar el SDK para las personalizaciones compatibles.

## Inventario de esta actualización

La comparación se hizo contra los recursos de ambas variantes del XCFramework (`ios-arm64` y `ios-arm64_x86_64-simulator`), en sus tres idiomas, y contra las dependencias indicadas al inicio:

| Grupo | Claves en la plantilla | Cambios |
| --- | ---: | --- |
| Become | 103 | Agregadas como referencia, con los valores del recurso `en` sin modificaciones. |
| CaptureUX | 40 | Agregadas `mbic_onboarding_title` y `mbic_onboarding_message`. |
| Face Liveness | 38 | Ya estaban completas; se conservaron los valores personalizados existentes. |
| Históricas de Identy | 163 | Se conservaron; se eliminaron seis definiciones repetidas manteniendo el último valor de cada clave. |
| **Total** | **344** | **105 claves nuevas; sin claves duplicadas.** |

La misma clave puede no mostrarse en todos los flujos. Este inventario corresponde a las versiones auditadas y debe revisarse cuando cambien los binarios o sus dependencias.
