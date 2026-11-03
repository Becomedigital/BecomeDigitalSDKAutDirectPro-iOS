// swift-tools-version: 6.4
import PackageDescription

let artifactVersion = "1.2.3"
let artifactChecksum = "750e81d1b99743717ba2ad89560263ddd8fc622924f9c797d757e33b4f78d5cd"
let artifactURL = "https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro-iOS/releases/download/\(artifactVersion)/BDIdentityVerification-\(artifactVersion).xcframework.zip"

let package = Package(
    name: "BecomeDigitalSDKAutDirectPro",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "BDIdentityVerification", targets: ["BDIdentityVerification", "LegacyPackageDependencies"])
    ],
    dependencies: [
        .package(url: "https://github.com/aws-amplify/amplify-swift", exact: "2.53.3"),
        .package(url: "https://github.com/aws-amplify/amplify-ui-swift-liveness", exact: "1.4.4"),
        .package(url: "https://github.com/BlinkID/capture-core-sp", exact: "1.4.3"),
        .package(url: "https://github.com/BlinkID/capture-ux-sp", exact: "1.4.3")
    ],
    targets: [
        .binaryTarget(name: "BDIdentityVerification", url: artifactURL, checksum: artifactChecksum),
        .target(
            name: "LegacyPackageDependencies",
            dependencies: [
                "BDIdentityVerification",
                .product(name: "Amplify", package: "amplify-swift"),
                .product(name: "FaceLiveness", package: "amplify-ui-swift-liveness"),
                .product(name: "CaptureCore", package: "capture-core-sp"),
                .product(name: "CaptureUX", package: "capture-ux-sp")
            ]
        )
    ]
)
