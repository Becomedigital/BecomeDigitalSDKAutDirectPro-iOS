# Language and optional local text overrides — iOS

## Standard integration

Become screen text is applied automatically from the contract. **Adding `Localizable.strings` or copying the template is not required to use the SDK or receive contract text updates.**

Use contract configuration for normal Become flow text changes, including introduction, consent, country and document selection, capture introductions, review, and results. Keep those phrases out of app resource files when they should receive later contract updates. Missing contract entries retain the SDK defaults.

Local resource customization primarily covers the internal interfaces of Microblink Capture UX and Amplify Face Liveness. It is not restricted to those providers: native loading/error labels and the supported Become screen overrides described below remain available for compatibility. The [resource template](Localizable.strings) is an optional reference, not an installation step or a catalog of every current screen phrase.

## When local resources are useful

| Need | Configuration |
| --- | --- |
| Normal Become flow copy, titles, instructions, and actions | Contract configuration for each language. |
| Intentionally replace a screen phrase from the app | A supported entry in the app target's `Localizable.strings`. |
| Native labels such as initial loading and certain errors | The native resource key read by that label. |
| Microblink Capture UX scanning guidance | Supported `mbic_*` resources for the integrated Capture UX version. |
| Amplify Face Liveness detector guidance | Supported `amplify_ui_liveness_*` resources for the integrated Amplify version. |

An app override takes priority for its key and can hide later contract updates. If the whole template was previously copied into the app, remove entries that should follow the contract and retain only intentional overrides.

## Precedence and language selection

Supported screen keys resolve individually: **app override → contract text for the current locale → base language → Spanish → SDK screen default**. Missing entries do not replace other keys. The SDK derives the locale from the iOS environment; `BDIVConfig` has no locale selector or localization-table parameter.

Current screens accept identifiers such as `intro.title`, `intro.cta`, `atdp.checkboxLabel`, and `countrySelection.searchPlaceholder`. A key affects only the phrase that reads it.

Some historical aliases remain supported, including `text_tittle_general_intro` for `intro.title`, and snake-case `atdp_` aliases. Other template entries belong to replaced screens and do not control the current SwiftUI views. Prefer a supported screen-specific identifier.

## Optional native component example

Add **only the supported component entries you intend to customize** to the app's `Localizable.strings`:

```text
"mbic_flip_document" = "Turn the document over";
"amplify_ui_liveness_challenge_connecting" = "Connecting…";
```

These entries target the Capture UX and Amplify interfaces, respectively. They do not replace the Become document-capture introduction or facial introduction text. Enable app target membership and create language variants such as `es.lproj/Localizable.strings` or `en.lproj/Localizable.strings` only for languages you customize. Rebuild the host app after local resource changes; rebuilding the XCFramework is unnecessary.

For an intentional Become override, use the supported screen identifier or native resource described above. Do not copy flow keys merely to configure the providers. A local override takes precedence only where the SDK reads that exact key.

## Native components

This distribution uses legacy Capture UX. Its instructions support compatible `mbic_*` native resource keys for the integrated version; the Become introduction copy has its own resolution path.

Amplify Face Liveness reads supported `amplify_ui_liveness_*` app entries and retains its own defaults for missing entries. Internal detector instructions and the Become facial introduction screen have separate localization paths; contract copy is not automatically mapped to every internal component phrase.

## Validation

Preserve key spelling, case, and existing format placeholders such as `%d%%` or `%@`. Native formatting paths may reject incompatible overrides. Check each customized language and verify that keys without overrides still follow the contract or their defaults. The integrating app performs functional validation on physical devices.
