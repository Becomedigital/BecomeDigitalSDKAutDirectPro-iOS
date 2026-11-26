// swift-tools-version: 6.4
import PackageDescription

let artifactVersion = "3.5.2-rc.1"
let artifactChecksum = "1648c2db1315798968d798a7e911dfd34831ad189cce0166432388560ffa9369"
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
