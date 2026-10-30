import UIKit
import SwiftUI
import BDIdentityVerification
import CaptureUX

struct BecomeSDKBridge: UIViewControllerRepresentable {
    let userId: String
    let onResult: (String) -> Void

    func makeUIViewController(context: Context) -> BecomeSDKPresenterViewController {
        BecomeSDKPresenterViewController(userId: userId, onResult: onResult)
    }

    func updateUIViewController(_ controller: BecomeSDKPresenterViewController, context: Context) {}
}

final class BecomeSDKPresenterViewController: UIViewController, BDIVDelegate {
    private let userId: String
    private let onResult: (String) -> Void
    private var identityVerification: BecomeDigitalSDK?
    private var hasStarted = false

    init(userId: String, onResult: @escaping (String) -> Void) {
        self.userId = userId
        self.onResult = onResult
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("Use init(userId:onResult:)")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.translatesAutoresizingMaskIntoConstraints = false
        indicator.startAnimating()
        view.addSubview(indicator)
        NSLayoutConstraint.activate([
            indicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            indicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !hasStarted else { return }
        hasStarted = true
        startOnboarding()
    }

    private func startOnboarding() {
        guard let url = Bundle.main.url(forResource: "Secrets", withExtension: "plist"),
              let data = try? Data(contentsOf: url),
              let values = try? PropertyListSerialization.propertyList(from: data, format: nil) as? [String: String],
              let clientId = values["clientId"], !clientId.isEmpty,
              let clientSecret = values["clientSecret"], !clientSecret.isEmpty,
              let contractId = values["contractId"], !contractId.isEmpty else {
            onResult(NSLocalizedString("credentials_missing", comment: ""))
            return
        }
        guard Bundle.main.url(forResource: "com.become.document.key", withExtension: "txt") != nil else {
            onResult(NSLocalizedString("license_missing", comment: ""))
            return
        }

        MBICCaptureUISDK.shared().customResourcesBundle = .main
        let config = BDIVConfig(
            clienId: clientId,
            clientSecret: clientSecret,
            contractId: contractId,
            documenTypes: [.DNI, .PASSPORT],
            userId: userId,
            flow: .Onboarding,
            debugLogsEnabled: true,
            themeMode: .system
        )
        identityVerification = BecomeDigitalSDK(bdivConfig: config, delegate: self)
        identityVerification?.startVerification()
    }

    func BDIVResponseSuccess(bdivResult: BDIdentityVerificationResponse) {
        DispatchQueue.main.async {
            self.onResult(String(format: NSLocalizedString("sdk_status", comment: ""),
                                 String(describing: bdivResult.responseStatus)))
        }
    }

    func BDIVResponseError(error: String) {
        DispatchQueue.main.async {
            self.onResult(String(format: NSLocalizedString("sdk_error", comment: ""), error))
        }
    }
}
