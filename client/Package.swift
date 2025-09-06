// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "LegalDify",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "LegalDify",
            targets: ["LegalDify"]
        )
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "LegalDify",
            dependencies: [],
            path: "LegalDify"
        ),
        .testTarget(
            name: "LegalDifyTests",
            dependencies: ["LegalDify"],
            path: "LegalDifyTests"
        )
    ]
)