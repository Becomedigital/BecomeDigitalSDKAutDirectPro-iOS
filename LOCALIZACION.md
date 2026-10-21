# Personalizar textos — iOS

## Implementación

1. Agregue [Localizable.strings](Localizable.strings) al target de su app. Si ya existe, copie solo las claves que quiera cambiar.
2. Edite el texto a la derecha de `=`; conserve el nombre de cada clave.
3. Para traducir, cree las variantes `es.lproj/Localizable.strings` y `en.lproj/Localizable.strings` desde Xcode.
4. Recompile la app. `BDIVConfig` no acepta un nombre de tabla: la SDK consulta `Localizable.strings` del target integrador.

Las claves que la app defina en `Localizable.strings` tienen prioridad para esas frases. Las demás conservan los textos asignados al contrato o los valores predeterminados de la SDK. El host no modifica textos mediante `BDIVConfig`.

## Ejemplo

```text
"text_start_btn" = "Comenzar";
"text_title_button_retry" = "Volver a intentar";
"text_title_document_error" = "Revisa las fotos de tu documento";
"text_btn_introduction_doc" = "Capturar documento";
"amplify_ui_liveness_get_ready_begin_check" = "Iniciar prueba de vida";
```

## Claves por pantalla

Una clave compartida cambia en todos los lugares donde se utiliza.
| Pantalla / uso | Claves |
| --- | --- |
| Inicio | `text_tittle_general_intro`, `text_sub_tittle_general_intro`, `text_selfie_intro_general`, `text_document_intr_general`, `text_start_btn` |
| Selección de país y documento | `text_tittle_selec_document`, `text_body_country`, `text_select_country`, `text_cancel_close`, `text_dni_selec_document`, `text_license`, `text_passport` |
| Introducción facial | `text_video_intro` |
| Captura documental | `text_tittle_intro_doc_front`, `text_btn_introduction_doc` |
| Vista previa | `text_info_preview`, `text_confirm_preview`, `text_retry_previe` |
| Carga y envío | `text_loader_init`, `text_loading`, `text_varification_title`, `text_varification_body`, `text_varification_buttom`, `text_info_upload`, `text_info_upload_document`, `text_document_validation` |
| Consulta de resultados | `text_progress_result`, `text_progress_delay_result`, `text_progress_delay_finish_result` |
| Error de documento y reintento | `text_title_document_error`, `text_sub_title_document_error`, `text_title_button_retry` |
| Creación de identidad y resultados: cierre facial, recaptura y reintento | Las claves `identity_error_*` de la plantilla. |
| Error general o validación fallida | `text_varification_title_error`, `text_varification_body_error`, `text_varification_title_compliance_error`, `text_varification_body_compliance_error`, `text_error_compliance_not_allowed`, `general_error`, `unknown_error` |
| Errores de conexión | `timeout_error`, `no_internet_error`, `connection_lost_error` |
| Permisos y privacidad | `tittle_permisiions_not_aut`, `camera_error_permissions`, `text_screen_recording_not_allowed` |
| Error facial | `liveness_detection_failed`, `error_low_confidence` |
| Error de configuración (callback) | `text_msn_error_config`, `error_clientid_empty`, `error_client_secret_empty`, `error_contractid_empty`, `error_userid_emty`, `error_vallidationtype_empty` |
| Resultado final | `text_finish`, `text_sub_tittle_finish`, `terminate_text` |
| Confirmar salida | `text_undo`, `text_cancel`, `text_tittle_undo`, `text_sub_tittle_undo`, `cancel_by_user` |

## Capture legacy and Face Liveness

Capture UX uses the `mbic_*` localization keys included in the template. Define the required entries in the host's Localizable.strings. Become's introduction, preview, and error screens continue to use the keys listed above.

`*` agrupa las claves con ese prefijo; copie el nombre completo desde la plantilla, nunca el asterisco.
| Pantalla / uso | Claves |
| --- | --- |
| Face Liveness: preparación y fotosensibilidad | `amplify_ui_liveness_get_ready_*` |
| Face Liveness: instrucciones de captura | `amplify_ui_liveness_challenge_*`, `amplify_ui_liveness_face_not_prepared_reason_*`, `amplify_ui_liveness_center_your_face_text` |
| Face Liveness: permisos y cierre | `amplify_ui_liveness_camera_*`, `amplify_ui_liveness_close_button_a11y` |

## Antes de entregar

- No duplique claves. Mantenga las instrucciones de cámara, accesibilidad y fotosensibilidad.
- Conserve `%d%%` en `text_info_upload` y `text_info_upload_document`, y `%@` en `liveness_detection_failed` y `error_low_confidence`. Si el formato no coincide, Become conserva el texto original.
- Pruebe la app en cada idioma después de recompilar. No necesita volver a generar el framework por un cambio de textos.
