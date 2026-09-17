# Personalizar textos — iOS

## Implementación

1. Agregue [Localizable.strings](Localizable.strings) al target de su app. Si ya existe, copie solo las claves que quiera cambiar.
2. Edite el texto a la derecha de `=`; conserve el nombre de cada clave.
3. Para traducir, cree las variantes `es.lproj/Localizable.strings` y `en.lproj/Localizable.strings` desde Xcode.
4. Configure Microblink con `customLocalizationFileName: "Localizable"` y recompile la app.

```swift
let config = BDIVConfig(
    clienId: clientId,
    clientSecret: clientSecret,
    contractId: contractId,
    documenTypes: [.DNI, .PASSPORT],
    userId: userId,
    customLocalizationFileName: "Localizable"
)
```

Este framework permite personalizar **Become, Microblink y Face Liveness**. Las claves no incluidas conservan el texto original. El parámetro anterior selecciona la tabla de Microblink; Become y Face Liveness usan `Localizable.strings`.

## Ejemplo

```text
"text_start_btn" = "Comenzar";
"text_title_button_retry" = "Volver a intentar";
"text_title_document_error" = "Revisa las fotos de tu documento";
"mbic_scan_the_front_side" = "Escanea el frente del documento";
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
| Error general o validación fallida | `text_varification_title_error`, `text_varification_body_error`, `text_varification_title_compliance_error`, `text_varification_body_compliance_error`, `text_error_compliance_not_allowed`, `general_error`, `unknown_error` |
| Errores de conexión | `timeout_error`, `no_internet_error`, `connection_lost_error` |
| Permisos y privacidad | `tittle_permisiions_not_aut`, `camera_error_permissions`, `text_screen_recording_not_allowed` |
| Error facial | `liveness_detection_failed`, `error_low_confidence` |
| Error de configuración (callback) | `text_msn_error_config`, `error_clientid_empty`, `error_client_secret_empty`, `error_contractid_empty`, `error_userid_emty`, `error_vallidationtype_empty` |
| Resultado final | `text_finish`, `text_sub_tittle_finish`, `terminate_text` |
| Confirmar salida | `text_undo`, `text_cancel`, `text_tittle_undo`, `text_sub_tittle_undo`, `cancel_by_user` |

## Captura Microblink y Face Liveness

`*` agrupa las claves con ese prefijo; copie el nombre completo desde la plantilla, nunca el asterisco.
| Pantalla / uso | Claves |
| --- | --- |
| Microblink: frente/reverso | `mbic_scan_*`, `mbic_flip_document` |
| Microblink: encuadre y calidad | `mbic_move_*`, `mbic_camera_angle_too_steep`, `mbic_document_too_close_to_edge`, `mbic_lightning_*`, `mbic_blur_detected`, `mbic_glare_detected`, `mbic_occluded`, `mbic_camer_orientation_*`, `mbic_torch_glare_tooltip_message` |
| Microblink: ayuda y preparación | `mbic_onboarding_*`, `mbic_tutorial_*`, `mbic_need_help_tooltip` |
| Microblink: cámara, red y botones | `mbic_camera_unavailable`, `mbic_camera_permission_error`, `mbic_camera_media_capture_error`, `mbic_camera_unable_to_resume_session`, `mbic_check_internet_connection`, `mbic_network_error`, `mbic_scanning_not_available`, `mbic_settings`, `mbic_done`, `mbic_cancel`, `mbic_back`, `mbic_next`, `mbic_ok`, `mbic_close` |
| Face Liveness: preparación y fotosensibilidad | `amplify_ui_liveness_get_ready_*` |
| Face Liveness: instrucciones de captura | `amplify_ui_liveness_challenge_*`, `amplify_ui_liveness_face_not_prepared_reason_*`, `amplify_ui_liveness_center_your_face_text` |
| Face Liveness: permisos y cierre | `amplify_ui_liveness_camera_*`, `amplify_ui_liveness_close_button_a11y` |

## Antes de entregar

- No duplique claves. Mantenga las instrucciones de cámara, accesibilidad y fotosensibilidad.
- Conserve `%d%%` en `text_info_upload` y `text_info_upload_document`, y `%@` en `liveness_detection_failed` y `error_low_confidence`. Si el formato no coincide, Become conserva el texto original.
- Los mensajes enviados por el servicio y los permisos del sistema no se cambian con estas claves.
- Las claves `there_already_a_record`, `splitValidationTypes`, `validation_type_video`, `_07` son internas; no las modifique. Become no admite su sobrescritura.
- El bloque de compatibilidad de la plantilla, incluidas las claves `identy_*`, `id_*`, `search_*` y de storyboard, pertenece a pantallas heredadas y no modifica el flujo actual.
- Pruebe la app en cada idioma después de recompilar. No necesita volver a generar el framework por un cambio de textos.
