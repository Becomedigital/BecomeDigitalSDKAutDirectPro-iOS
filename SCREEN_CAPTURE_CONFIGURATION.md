# Screen capture configuration for the iOS SDK

This guide applies to the `BDIdentityVerification.xcframework` included in this repository. The XCFramework was built from source commit `54ba9b8421de9f9be4169cd12a2294a272946c10` using the production Release scheme `BDIdentityVerification_PROD`.

## Behavior change

`BDIVConfig.preventScreenCapture` now defaults to `false`. Earlier distributed builds defaulted to `true`. An application that omits the argument now allows screenshots and screen recording of SDK content. This default is the same in Debug and Release builds. An application that passes an explicit value keeps the behavior it requested.

| Value | SDK behavior |
| --- | --- |
| `false` (default) | The SDK does not apply its screen capture protection or recording blocker to its UI. |
| `true` | The SDK protects its UI during screenshots and displays a blocking view while screen recording is detected. |

The option applies to the screens presented by the Become SDK while its verification flow is active. It does not configure unrelated screens in the host application or override protection applied independently by the operating system or another component.

## Enable protection explicitly

Pass `preventScreenCapture: true` when constructing `BDIVConfig`, before calling `startVerification()`:

```swift
import BDIdentityVerification

let config = BDIVConfig(
    clienId: "YOUR_CLIENT_ID",
    clientSecret: "YOUR_CLIENT_SECRET",
    contractId: "YOUR_CONTRACT_ID",
    documenTypes: [.DNI, .PASSPORT],
    userId: "YOUR_USER_ID",
    preventScreenCapture: true
)

let verification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
verification.startVerification()
```

Omit the argument or pass `false` to use the new default. `preventScreenCapture` is fixed for a `BDIVConfig` instance; create a new configuration for a later flow that needs a different value. The setting is available for both `.Onboarding` and `.Authentication`.

## Migration from an earlier XCFramework

1. Review every `BDIVConfig` creation in the host application. Calls that omit `preventScreenCapture` change from protected to unprotected when this XCFramework is integrated.
2. Add `preventScreenCapture: true` wherever the previous protected behavior must continue. Calls that already pass `true` or `false` need no change.
3. Rebuild the host application with this XCFramework. Continue to embed and sign it in the application target as described in the main README.
4. On a physical device, check screenshots and screen recording during document capture, face liveness, cancellation, and return to the host application. Run this check once with the default and once with `true` if your application supports both modes.

Screen capture policy should be chosen by the integrator based on the application's privacy requirements. This flag controls the SDK presentation; it is not a substitute for application-wide data handling or device policy.

## Artifact verification

The public Swift interface inside each XCFramework slice exposes a `preventScreenCapture` argument with a `false` default in the `BDIVConfig` initializer. The framework contains an iOS device slice (`arm64`) and an iOS simulator slice (`arm64` and `x86_64`), both at version `1.2.3`. Functional capture and face liveness require the integrator's licensed application and a physical device.

SHA-256 checksums of the framework executables:

| Slice | SHA-256 |
| --- | --- |
| iOS device | `28300403cf9113839f4e3b75ad53bf8ce983ce21a147ec5984e4dc5e37c7dc68` |
| iOS simulator | `80b8d10ed52584edce3763c0e9a2738e2980a5eef7187c90c80ee4ab111a4f74` |
