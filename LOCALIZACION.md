# Native component text — iOS

## Become flow text

Become titles, instructions, consent, country/document selection, introductions, review and results are managed by the contract configuration. Local translation files are not required to receive those texts. Missing entries retain the SDK defaults.

This guide and its examples intentionally list native component and technical SDK keys only. Remove old flow entries from app resources when those phrases should follow contract updates. A supported local override can pin a phrase and hide later updates; do not copy the whole template.

## Native technical SDK labels

These labels still read local resources rather than contract text. The examples retain verified startup `text_loader_init`; network errors `timeout_error`, `no_internet_error` and `connection_lost_error`; progress `text_info_upload` and `text_info_upload_document` (preserve `%d%%`).

These are not flow title/action configuration keys.

## Supported components

| Component | Verified version | Local keys |
| --- | --- | --- |
| Microblink Capture UX | 1.4.3 | `mbic_*` |
| Amplify Face Liveness | 1.4.4 / 1.4.5 | `amplify_ui_liveness_*` |

This distribution retains Capture Legacy. BlinkID `mb_*` / `mb_blinkid_*` resources do not apply to its capture interface. Names differ across platforms; use this distribution’s keys.

## Optional customization

Add only the entries you intend to customize to the app target’s `Localizable.strings`:

```text
"mbic_flip_document" = "Turn the document over";
"amplify_ui_liveness_challenge_connecting" = "Connecting…";
```

Capture UX uses supported app `Localizable` entries with a native fallback. Amplify reads the main app bundle at initialization and retains its native defaults for missing keys. The integrated Face Liveness version has no supported public API to inject contract text inside its iOS detector. SDK-owned facial introduction, feedback and review text still follows the contract.

Enable app target membership and create language variants such as `es.lproj/Localizable.strings` and `en.lproj/Localizable.strings`. See the [optional native key reference](Localizable.strings).

## Validation

Preserve exact key names, capitalization, format placeholders, and the meaning of camera safety and photosensitivity instructions. Edit only required values. Rebuild the app after resource changes; rebuilding the SDK is unnecessary. Validate customized languages on physical devices. `BDIVConfig` does not select a localization table or configure Become flow text.
