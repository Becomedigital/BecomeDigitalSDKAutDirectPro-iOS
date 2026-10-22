# Text customization — iOS

## Per-key precedence

For the current SDK screens, an explicit app entry in `Localizable.strings` takes priority for that key. Otherwise, the SDK uses the contract text for the requested locale, its base language, Spanish, and finally the bundled screen default. Missing entries do not replace unrelated text.

`BDIVConfig` has no text-table or custom-localization-file parameter. Use the app target's standard `Localizable.strings` table. Copy only the entries you intend to override from the [resource template](Localizable.strings); copying the whole template can replace contract text unintentionally.

## Current screen keys

Use the exact, case-sensitive `namespace.key` identifier. Examples:

```text
"intro.title" = "Welcome";
"intro.welcome" = "Let's verify your identity";
"intro.body" = "Have your original identity document ready.";
"intro.cta" = "Start";
"atdp.title" = "Personal data processing";
"atdp.checkboxLabel" = "I have read and accept the privacy notice.";
"atdp.accept" = "Accept and continue";
"atdp.decline" = "Decline";
"countrySelection.searchPlaceholder" = "Search country…";
```

| Screen | Useful identifiers |
| --- | --- |
| Introduction | `intro.title`, `intro.welcome`, `intro.body`, `intro.cta`, `intro.ctaAriaLabel` |
| Optional introduction header | `intro.header.reminder`, `intro.header.description` |
| Data processing notice | `atdp.title`, `atdp.subtitle`, `atdp.markdown`, `atdp.contentLabel`, `atdp.checkboxLabel`, `atdp.accept`, `atdp.decline` |
| Country selection | `countrySelection.title`, `countrySelection.subtitle`, `countrySelection.searchPlaceholder` |
| Document selection | `documentType.title` |
| Document capture and preview | `capture.title`, `capture.previewTitle`, `capture.previewDescription`, `capture.usePhoto` |
| Facial instructions | `liveness.title`, `liveness.instruction1` through `liveness.instruction4`, `liveness.start` |
| Shared navigation | `common.continue`, `common.back`, `common.close`, `common.retry` |
| Result | `result.title`, `result.description` |

Each key affects only the screen that reads it. The legacy aliases `text_tittle_general_intro`, `text_sub_tittle_general_intro`, `text_start_btn`, `text_tittle_selec_document`, `text_body_country`, `text_tittle_intro_doc_front`, `text_video_intro`, `text_finish`, and `text_sub_tittle_finish` remain mapped where supported. `text_start_btn` is shared by the introduction action and common continuation labels; use a scoped key when only one label should change. Data-processing keys also support the `atdp_` snake-case aliases, such as `atdp_checkbox_label`.

## Native component and error text

The template also contains native resource keys used by error messages and supported component screens:

```text
"identity_error_documentFront" = "Capture the front again with all edges visible.";
"text_title_button_retry" = "Try again";
"mbic_scan_the_front_side" = "Scan the front of your document";
"amplify_ui_liveness_get_ready_begin_check" = "Start the liveness check";
```

Capture UX uses supported `mbic_*` keys. Amplify Face Liveness uses its supported `amplify_ui_liveness_*` keys. Legacy template entries do not add screens or change the contract's enabled steps.

## Integration checklist

1. Add the selected entries to the app target's `Localizable.strings` and enable target membership.
2. Create language variants, for example `es.lproj/Localizable.strings` and `en.lproj/Localizable.strings`.
3. Keep key spelling and case, even for historical names. Avoid duplicate entries.
4. Preserve format placeholders, including `%d%%` in progress text and `%@` in formatted error labels. Incompatible formats fall back to the original SDK text.
5. Rebuild the host app and validate the affected screens in each supported language on a physical device. Regenerating the XCFramework is not necessary for app resource changes.
