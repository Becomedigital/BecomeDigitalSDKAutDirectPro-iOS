# SwiftUI integration example

This app shows how to start the distributed iOS SDK from SwiftUI. `BecomeSwiftUIScreen` presents `BecomeSDKBridge`, which retains a UIKit view controller while the SDK is active and receives `BDIVDelegate` callbacks. The app also handles background URL session events and provides English, Spanish, and Latin American Spanish resources for the host screen and supported native components.

The repository contains no client credentials or capture license for this example. A contract with Become, credentials for that contract, and a license issued for your app identifier are required to complete a verification. Without them, the example builds but shows a missing configuration message when you try to start the SDK.

## Prepare your local app

1. Read the [installation guide](../../README.md#installation-and-dependencies) and use Xcode 27 or later with iOS 16 or later.
2. Copy `App/Secrets.example.plist` to `App/Secrets.plist`. Enter the `clientId`, `clientSecret`, and `contractId` supplied for your integration. The real file is ignored by Git.
3. Place the capture license supplied for your app at `App/com.become.document.key.txt`. This file is also ignored by Git. Use a license valid for the app identifier and environment you will test.
4. Set your authorized app identifier and regenerate the project:

   ```bash
   BECOME_DEMO_BUNDLE_ID=com.yourcompany.yourapp ruby generate_project.rb
   ```

   The generator requires the `xcodeproj` Ruby gem. It includes the two private files as bundle resources only when they exist. Regenerate the project after adding or removing either file.
5. Open `BecomeSwiftUIDemo.xcodeproj`, select your signing team, and build for a physical iPhone. The app targets iOS 16 or later. Enter a user ID and tap **Start onboarding**.

The repository's `BDIdentityVerification.xcframework` is referenced directly; there is no second copy in this example. The project pins the Swift packages to the versions in the [installation guide](../../README.md#installation-and-dependencies). If you change the generated project locally, review its resource membership before sharing it; never commit `Secrets.plist`, the license, or a built app.

`BDIVConfig.debugLogsEnabled` is enabled for support diagnostics. Logs can contain personal information from a test session. The [localization guide](../../LOCALIZACION.md) explains which text is supplied by the contract and which native text can be translated in the app. The [logging guide](../../LOGGING.md) describes the supported diagnostics.

Document capture and facial verification require a physical device and valid integration details. A successful simulator build confirms compilation and resource packaging only.
