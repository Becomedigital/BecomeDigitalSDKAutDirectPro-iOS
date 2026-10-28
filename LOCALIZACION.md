# Localización de la SDK de iOS

La SDK utiliza los textos de verificación asociados a tu contrato. No necesitas agregar archivos locales para los títulos, consentimiento, selección de país y documento, introducciones, revisión o resultado. Si falta un texto del contrato, se conserva el valor disponible en la SDK.

Puedes personalizar las indicaciones de captura y los mensajes de carga y conexión que se enumeran en esta guía.

## Agregar traducciones a tu aplicación

1. Crea o edita `Localizable.strings` en el destino de tu aplicación.
2. Agrega únicamente las claves que deseas personalizar.
3. Crea las variantes de idioma que necesites, por ejemplo `es.lproj/Localizable.strings` y `en.lproj/Localizable.strings`.
4. Comprueba la pertenencia de los archivos al destino de la aplicación.

Ejemplo:

```text
"mbic_flip_document" = "Voltea el documento";
"amplify_ui_liveness_challenge_connecting" = "Conectando…";
"text_loader_init" = "Iniciando…";
```

Para aplicar los textos de captura de documento, selecciona los recursos de la aplicación antes de iniciar la verificación:

```swift
import CaptureUX

MBICCaptureUISDK.shared().customResourcesBundle = .main
```

Las claves no incluidas conservan las traducciones del componente. Las indicaciones de captura facial leen `Localizable.strings` de la aplicación al inicializarse.

## Claves disponibles

Estas claves corresponden a CaptureUX 1.4.3 y Face Liveness 1.4.4, las dependencias de esta entrega. Utiliza los nombres exactos de esta plataforma. La [plantilla en español](Localizable.strings) incluye todas las claves siguientes; copia solo las que quieras cambiar.

### Carga, progreso y conexión

| Clave | Ejemplo de texto |
| --- | --- |
| `text_loader_init` | Iniciando… |
| `timeout_error` | La conexión tardó demasiado. Inténtalo nuevamente. |
| `no_internet_error` | No tienes conexión a internet. Verifica tu red. |
| `connection_lost_error` | Se perdió la conexión a internet. Inténtalo nuevamente. |
| `text_info_upload` | Estamos enviando tu información… %d%% |
| `text_info_upload_document` | Estamos enviando tus documentos… %d%% |

Conserva `%d%%` en los dos mensajes de progreso para mostrar el porcentaje correctamente.

### Captura de documento

| Clave | Ejemplo de texto |
| --- | --- |
| `mbic_back` | Volver |
| `mbic_blur_detected` | Mantén el documento y el teléfono quietos |
| `mbic_camer_orientation_unsuitable` | Gira el teléfono o el documento |
| `mbic_camer_orientation_unsuitable_animation` | Gira el documento o coloca el teléfono en horizontal |
| `mbic_camera_angle_too_steep` | Mantén el documento paralelo al teléfono |
| `mbic_camera_media_capture_error` | No se pudo realizar la captura |
| `mbic_camera_permission_error` | La aplicación no tiene permiso para usar la cámara. Actualiza los ajustes de privacidad. |
| `mbic_camera_unable_to_resume_session` | No se pudo reanudar la sesión |
| `mbic_camera_unavailable` | Cámara no disponible |
| `mbic_cancel` | Cancelar |
| `mbic_check_internet_connection` | Verifica la conexión a internet |
| `mbic_close` | Cerrar |
| `mbic_document_too_close_to_edge` | Mantén el documento completamente visible |
| `mbic_done` | Listo |
| `mbic_flip_document` | Voltea el documento |
| `mbic_glare_detected` | Inclina o mueve el documento para eliminar los reflejos |
| `mbic_lightning_too_bright` | Busca un lugar con menos luz |
| `mbic_lightning_too_dark` | Busca un lugar más iluminado |
| `mbic_move_closer` | Acércate |
| `mbic_move_farther` | Aléjate |
| `mbic_need_help_tooltip` | ¿Necesitas ayuda? |
| `mbic_network_error` | Error de conexión |
| `mbic_next` | Siguiente |
| `mbic_occluded` | Mantén el documento completamente visible |
| `mbic_ok` | Aceptar |
| `mbic_onboarding_field_visible_details` | Asegúrate de que el documento esté bien iluminado y de que todos sus campos sean visibles en la cámara. |
| `mbic_onboarding_field_visible_title` | Mantén todos los detalles visibles |
| `mbic_onboarding_message` | Para obtener mejores resultados, coloca el teléfono en horizontal al escanear el documento. Sigue la imagen de ejemplo y comprueba que todos los campos sean visibles. |
| `mbic_onboarding_title` | Coloca el teléfono en horizontal |
| `mbic_scan_the_back_side` | Escanea el lado posterior del documento |
| `mbic_scan_the_front_side` | Escanea el lado frontal del documento |
| `mbic_scanning_not_available` | Escaneo no disponible |
| `mbic_settings` | Ajustes |
| `mbic_torch_glare_tooltip_message` | Evita los reflejos de la linterna.<br>Mueve suavemente el documento para eliminarlos. |
| `mbic_tutorial_fields_visible_details` | No cubras el documento con los dedos, incluidas las líneas inferiores. Evita los reflejos del holograma sobre sus campos. |
| `mbic_tutorial_fields_visible_title` | Mantén todos los campos visibles |
| `mbic_tutorial_harsh_light_details` | Evita la luz directa intensa: puede reflejarse en el documento e impedir su lectura. Si no puedes leerlo, la cámara tampoco podrá hacerlo. |
| `mbic_tutorial_harsh_light_title` | Evita la luz intensa |
| `mbic_tutorial_keep_still_details` | Mantén quietos el teléfono y el documento durante el escaneo. El movimiento puede desenfocar la imagen e impedir la lectura de los datos. |
| `mbic_tutorial_keep_still_title` | No te muevas durante el escaneo |

### Captura facial

| Clave | Ejemplo de texto |
| --- | --- |
| `amplify_ui_liveness_camera_permission_button_description` | Es posible que debas permitir el acceso a la cámara en los ajustes, cerrar la aplicación y volver a intentarlo. |
| `amplify_ui_liveness_camera_permission_button_header` | No se puede acceder a la cámara |
| `amplify_ui_liveness_camera_permission_button_title` | Cambiar ajustes de cámara |
| `amplify_ui_liveness_camera_permission_page_title` | Prueba de vida |
| `amplify_ui_liveness_camera_setting_alert_message` | Permite el acceso a la cámara en los ajustes. |
| `amplify_ui_liveness_camera_setting_alert_not_now_button_text` | Ahora no |
| `amplify_ui_liveness_camera_setting_alert_title` | Cambiar ajustes de cámara |
| `amplify_ui_liveness_camera_setting_alert_update_setting_button_text` | Actualizar ajustes |
| `amplify_ui_liveness_center_your_face_text` | Centra tu rostro |
| `amplify_ui_liveness_challenge_cancel_a11y` | Cancelar verificación |
| `amplify_ui_liveness_challenge_connecting` | Conectando… |
| `amplify_ui_liveness_challenge_instruction_hold_face_during_countdown` | Mantén la posición del rostro durante la cuenta regresiva. |
| `amplify_ui_liveness_challenge_instruction_hold_face_during_freshness` | Mantén el rostro dentro del óvalo durante la detección con luces de colores. |
| `amplify_ui_liveness_challenge_instruction_hold_still` | No te muevas |
| `amplify_ui_liveness_challenge_instruction_move_face_back` | Aléjate |
| `amplify_ui_liveness_challenge_instruction_move_face_closer` | Acércate |
| `amplify_ui_liveness_challenge_instruction_move_face_in_front_of_camera` | Coloca tu rostro frente a la cámara |
| `amplify_ui_liveness_challenge_instruction_multiple_faces_detected` | Solo un rostro por verificación |
| `amplify_ui_liveness_challenge_recording_indicator_label` | GRAB. |
| `amplify_ui_liveness_challenge_verifying` | Verificando |
| `amplify_ui_liveness_close_button_a11y` | Cerrar |
| `amplify_ui_liveness_face_not_prepared_reason_face_too_close` | Aleja un poco el rostro |
| `amplify_ui_liveness_face_not_prepared_reason_move_face_closer` | Acércate |
| `amplify_ui_liveness_face_not_prepared_reason_move_face_left` | Mueve el rostro hacia la izquierda |
| `amplify_ui_liveness_face_not_prepared_reason_move_face_right` | Mueve el rostro hacia la derecha |
| `amplify_ui_liveness_face_not_prepared_reason_move_to_brighter_area` | Busca un lugar más iluminado |
| `amplify_ui_liveness_face_not_prepared_reason_move_to_dimmer_area` | Busca un lugar con menos luz |
| `amplify_ui_liveness_face_not_prepared_reason_multiple_faces` | Solo un rostro por verificación |
| `amplify_ui_liveness_face_not_prepared_reason_no_face` | Coloca tu rostro frente a la cámara |
| `amplify_ui_liveness_face_not_prepared_reason_not_in_oval` | Mueve el rostro para que quede dentro del óvalo |
| `amplify_ui_liveness_face_not_prepared_reason_pendingCheck` | Sin texto visible. |
| `amplify_ui_liveness_get_ready_begin_check` | Iniciar verificación de video |
| `amplify_ui_liveness_get_ready_page_title` | Prueba de vida |
| `amplify_ui_liveness_get_ready_photosensitivity_description` | Esta verificación muestra luces de diferentes colores. Ten precaución si eres fotosensible. |
| `amplify_ui_liveness_get_ready_photosensitivity_dialog_description` | Algunas personas pueden experimentar convulsiones epilépticas al exponerse a luces de colores intermitentes. Ten precaución si tú o alguien de tu familia presenta una condición convulsiva. |
| `amplify_ui_liveness_get_ready_photosensitivity_dialog_title` | Advertencia de fotosensibilidad |
| `amplify_ui_liveness_get_ready_photosensitivity_icon_a11y` | Información sobre fotosensibilidad |
| `amplify_ui_liveness_get_ready_photosensitivity_title` | Advertencia de fotosensibilidad |

## Recomendaciones

- Mantén los nombres, mayúsculas, saltos de línea y marcadores de formato de cada clave.
- Conserva el significado de los avisos de permisos, seguridad de captura y fotosensibilidad.
- Verifica las traducciones en un dispositivo físico con el idioma que utilizará tu usuario.
- Actualiza los textos generales de verificación en la configuración del contrato. `BDIVConfig` permite elegir `themeMode`, pero no establece una tabla de traducciones ni textos del flujo.

Volver a la [guía de integración](README.md).
