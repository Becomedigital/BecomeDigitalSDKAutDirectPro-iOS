# Become iOS SDK — Capture legacy

This guide matches the `BDIdentityVerification.xcframework` distributed on `feature/mobile-contract-parity`. It provides SwiftUI verification screens with onboarding and authentication, typed results, contract-controlled appearance, and Microblink Capture legacy document capture.

## Validated versions

| Component | Version |
| --- | --- |
| Become framework | 1.2.3 |
| Minimum iOS | 16.0 |
| Validated Xcode | 27.0 (27A266a) |
| Framework compiler | Apple Swift 6.4, Swift 5 language mode |
| Amplify Swift | 2.53.3 |
| Amplify UI Swift Liveness | 1.4.4 |
| CaptureCore | 1.4.3 |
| CaptureUX | 1.4.3 |

Use Xcode 27.0 or a compatible newer toolchain capable of reading the supplied Swift 6.4 module interfaces. The XCFramework contains an arm64 device slice and arm64/x86_64 simulator slices. Camera and identity checks require a physical device.

The supplied framework is the production build. `BDIVConfig` has no environment selector. A separate development build and a valid license for its application identifier are required when testing another environment.

## Installation and dependencies

1. Add `BDIdentityVerification.xcframework` to the application target and select **Embed & Sign**.
2. In Xcode, use **File > Add Package Dependencies** and select **Exact Version** for each package below.

| Package URL | Exact version | App target products |
| --- | --- | --- |
| https://github.com/aws-amplify/amplify-swift | 2.53.3 | `Amplify` |
| https://github.com/aws-amplify/amplify-ui-swift-liveness | 1.4.4 | `FaceLiveness` |
| https://github.com/BlinkID/capture-core-sp | 1.4.3 | `CaptureCore` |
| https://github.com/BlinkID/capture-ux-sp | 1.4.3 | `CaptureUX` |

3. Embed and sign `BDIdentityVerification.framework`, `CaptureCore.framework`, and `CaptureUX.framework`. Confirm that all three are present in the built app's `Frameworks` directory. Let Swift Package Manager manage the other package products and their transitive dependencies.
4. Remove BlinkID Core/UX migration packages when integrating this Capture legacy build. Keep versions aligned if the host already uses Amplify.
5. Add the license issued for the application's Bundle Identifier as **`com.become.document.key.txt`**. Enable app target membership and include it in **Copy Bundle Resources**. Keep license contents out of source control.

All listed dependencies remain required when a particular contract omits facial capture.

## Permissions

Add a camera usage description to the app's `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Camera access is required to verify your identity.</string>
```

If the integration uses optional location collection, also declare `NSLocationWhenInUseUsageDescription`. Denying location does not block verification.

## Initialization

The delegate must be a `UIViewController` implementing `BDIVDelegate`. Retain the SDK instance while verification is active. The public spellings `clienId` and `documenTypes` are retained for compatibility.

```swift
import UIKit
import BDIdentityVerification

final class ViewController: UIViewController, BDIVDelegate {
    private var identityVerification: BecomeDigitalSDK?

    func startOnboarding() {
        let config = BDIVConfig(
            clienId: "YOUR_CLIENT_ID",
            clientSecret: "YOUR_CLIENT_SECRET",
            contractId: "YOUR_CONTRACT_ID",
            documenTypes: [.DNI, .PASSPORT, .DRIVERLICENSE],
            userId: "YOUR_USER_ID",
            flow: .Onboarding,
            themeMode: .system
        )
        identityVerification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
        identityVerification?.startVerification()
    }

    func BDIVResponseSuccess(bdivResult: BDIdentityVerificationResponse) {
        guard bdivResult.responseStatus == .SUCCES else { return }
        if let started = bdivResult.onboarding { _ = started.userId }
        if let final = bdivResult.verification { _ = final.urlGetData }
        if let authentication = bdivResult.authentication {
            // Evaluate the authentication decision separately from SDK success.
            _ = authentication.result
        }
    }

    func BDIVResponseError(error: String) {
        // Restore the host UI and offer a new user-initiated attempt.
    }
}
```

### Public configuration

| Parameter | Default | Meaning |
| --- | --- | --- |
| `clienId`, `clientSecret`, `contractId` | Required arguments | Nonempty client credentials and contract identifier. |
| `userId` | Required argument | Nonempty for `.Authentication`; onboarding also accepts an empty string. |
| `documenTypes` | Required argument | `.DNI`, `.PASSPORT`, `.DRIVERLICENSE`. The contract filters this list. An empty list uses the contract's available types. |
| `flow` | `.Onboarding` | `.Onboarding` or `.Authentication`. |
| `performVerificationCheck` | `true` | Wait for final onboarding confirmation. Set `false` to return the creation result directly. |
| `pollingMaxAttempts` | `0` | Maximum result checks; `0` means no attempt limit. |
| `pollingTimeout` | `2` seconds | Timeout for each result check. For slow connections, use a larger value such as `30`. |
| `debugLogsEnabled` | `false` | Enable optional client diagnostics. |
| `preventScreenCapture` | `false` | Enable the SDK's screen-capture protection when `true`. |
| `country`, `state` | `nil` | Optional two-letter country code or comma-separated country list; optional US postal state code. |
| `nationalIdType`, `documentNumber` | `nil` | Optional prefilled document details. |
| `nationalIdTypeChoices` | `[]` | Optional document subtype choices. |
| `themeMode` | `.system` | `.light`, `.dark`, or the device's preferred appearance. |

For authentication, use `flow: .Authentication`, an existing nonempty `userId`, and `documenTypes: []` when documents are not required. Create a new configuration to change immutable parameters for another run.

### Documents and presentation

The SDK displays the steps and document types available for the contract. Supplying fewer document types restricts the requested list to supported types; when there is no overlap, the SDK uses the contract list. A single document type is still displayed for confirmation. Passport capture uses the front; other required sides follow the contract.

Complete frames are used for document uploads. Cropped, perspective-corrected images are used for preview; if no crop is available, the preview can show the complete frame. Full-frame uploads preserve the image bounds while applying JPEG encoding and size limits.

The host selects `themeMode`. Contract presentation and screen text are applied automatically; `BDIVConfig` has no design or localization-table settings. Standard integration does not require copying translation files. App text overrides are optional and apply only to supported keys; see [language and optional local text overrides](LOCALIZACION.md).

An animated loader remains visible until the first configured screen is ready. Its initial color uses the host's `AccentColor` or inherited tint. Document-only contracts do not require a facial result to complete.

## Typed results and errors

`BDIVResponseSuccess` receives `BDIdentityVerificationResponse`, containing `responseStatus`, `message`, and optional flow-specific objects:

| Object | Public fields | When to inspect it |
| --- | --- | --- |
| `onboarding` | `code`, `message`, `urlResource`, `userId` | Direct creation result when `performVerificationCheck` is `false`. Creation is not final approval. |
| `verification` | `urlGetData` | Confirmed onboarding result when waiting for completion. |
| `authentication` | `company`, `confidence`, `executionId`, `liveness`, `result`, `userId` | Authentication result; evaluate the Boolean `result` separately. |

The response object provides `toJson()`. Do not expect a response dictionary. `SUCCES` retains its historical spelling; other declared statuses are `ERROR`, `PENDING`, and `NOFOUND`. Errors and user cancellation are delivered through `BDIVResponseError(error:)`. Message text is not a stable error code. See [error handling](ERRORES.md).

## Additional guides

- [Language and optional local text overrides](LOCALIZACION.md)
- [Optional client diagnostics](LOGGING.md)
- [Screen-capture protection](SCREEN_CAPTURE_CONFIGURATION.md)
- [Background session events](CARGAS_SEGUNDO_PLANO.md)

Before release, validate camera permissions, the licensed app identifier, both requested document sides, cancellation, and the configured flow on a physical device.
