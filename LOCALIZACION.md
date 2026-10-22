# Language and optional local text overrides — iOS

## Standard integration

Become screen text is applied automatically from the contract. **Adding `Localizable.strings` or copying the template is not required to use the SDK or receive contract text updates.**

This guide remains useful for intentional app overrides, native messages, and capture components. The [resource template](Localizable.strings) is a compatibility reference, not an installation step or a catalog of every phrase displayed by the current screens.

## When local resources are useful

| Need | Configuration |
| --- | --- |
| Normal Become flow copy, titles, instructions, and actions | Contract configuration for each language. |
| Intentionally replace a screen phrase from the app | A supported entry in the app target's `Localizable.strings`. |
| Native labels such as initial loading and certain errors | The native resource key read by that label. |
| Internal document capture and facial detector instructions | Resources supported by that native component and version. |

An app override takes priority for its key and can hide later contract updates. If the whole template was previously copied into the app, remove entries that should follow the contract and retain only intentional overrides.

## Precedence and language selection

Supported screen keys resolve individually: **app override → contract text for the current locale → base language → Spanish → SDK screen default**. Missing entries do not replace other keys. The SDK derives the locale from the iOS environment; `BDIVConfig` has no locale selector or localization-table parameter.

Current screens accept identifiers such as `intro.title`, `intro.cta`, `atdp.checkboxLabel`, and `countrySelection.searchPlaceholder`. A key affects only the phrase that reads it.

Some historical aliases remain supported, including `text_tittle_general_intro` for `intro.title`, and snake-case `atdp_` aliases. Other template entries belong to replaced screens and do not control the current SwiftUI views. Prefer a supported screen-specific identifier.

## Optional example

Add **only intentional overrides** to the app's `Localizable.strings`:

```text
"intro.cta" = "Start verification";
"countrySelection.searchPlaceholder" = "Search issuing country…";
"text_loader_init" = "Loading…";
"identity_error_documentFront" = "Capture the front again, fully visible and in focus.";
```

The first two are screen keys; the others are native loading and error keys. Enable app target membership and create language variants such as `es.lproj/Localizable.strings` or `en.lproj/Localizable.strings` only for languages you customize. Rebuild the host app after local resource changes; rebuilding the XCFramework is unnecessary.

## Native components

This distribution uses legacy Capture UX. Its instructions support compatible `mbic_*` native resource keys for the integrated version; the Become introduction copy has its own resolution path.

Amplify Face Liveness reads supported `amplify_ui_liveness_*` app entries and retains its own defaults for missing entries. Internal detector instructions and the Become facial introduction screen have separate localization paths; contract copy is not automatically mapped to every internal component phrase.

## Validation

Preserve key spelling, case, and existing format placeholders such as `%d%%` or `%@`. Native formatting paths may reject incompatible overrides. Check each customized language and verify that keys without overrides still follow the contract or their defaults. The integrating app performs functional validation on physical devices.
