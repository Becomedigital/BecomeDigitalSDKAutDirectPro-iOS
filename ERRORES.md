# Error and result handling — iOS

## Public callbacks

| Callback or status | Host action |
| --- | --- |
| `BDIVResponseSuccess(bdivResult:)` with `.SUCCES` | Inspect the optional object for the completed SDK operation. For authentication, evaluate `authentication.result` separately. |
| A declared `PENDING` or `NOFOUND` result | Do not treat it as approval. |
| `BDIVResponseError(error:)` | Restore the host UI and offer a new user-initiated attempt. User cancellation also uses this callback. |

`SUCCES` retains its historical spelling. `error` and response `message` values are descriptive text, not stable error codes. The `onboarding`, `authentication`, and `verification` objects can be `nil`.

With `performVerificationCheck: false`, an `onboarding` object confirms creation, not final approval. With final-result checking enabled, inspect the `verification` object. Document-only flows do not require a facial result.

The SDK presents its available capture and retry actions inside its own UI. The host does not receive a callback for every capture attempt.

## Integration checks

- **Configuration:** provide nonempty client credentials and a contract ID. Authentication also requires a nonempty existing user ID. An empty document array uses the contract's available document types.
- **Camera:** verify the device and `NSCameraUsageDescription`, then allow a new attempt after permissions are corrected.
- **Capture license:** verify `com.become.document.key.txt`, app target membership, and the licensed Bundle Identifier.
- **Missing module or framework:** use the exact package versions in the [README](README.md), the compatible Xcode toolchain, and all three required embedded frameworks.
- **Connection:** allow a new user-initiated attempt after connectivity returns. Adjust `pollingTimeout` when individual result checks time out; `pollingMaxAttempts` controls the number of checks.
- **Incomplete capture:** allow the SDK to request the required sides again. A cropped preview is not a substitute for a missing full-frame capture.

Do not branch on localized message text to approve an identity or trigger automatic retries. When requesting support, provide the SDK version, device, visible step, and relevant [client diagnostics](LOGGING.md), excluding credentials and images.
