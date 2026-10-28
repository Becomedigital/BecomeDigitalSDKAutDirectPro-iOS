import SwiftUI

struct BecomeSwiftUIScreen: View {
    @State private var userId = ""
    @State private var activeUserId = ""
    @State private var status = NSLocalizedString("status_ready", comment: "")
    @State private var showingSDK = false

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("host_title")
                .font(.title2)

            TextField("user_id_label", text: $userId)
                .textFieldStyle(.roundedBorder)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()

            Button("start_onboarding") {
                let id = userId.trimmingCharacters(in: .whitespacesAndNewlines)
                guard !id.isEmpty else {
                    status = NSLocalizedString("user_id_required", comment: "")
                    return
                }
                activeUserId = id
                status = NSLocalizedString("status_starting", comment: "")
                showingSDK = true
            }

            Text(status)
                .accessibilityIdentifier("sdkStatus")

            Spacer()
        }
        .padding(24)
        .sheet(isPresented: $showingSDK) {
            BecomeSDKBridge(userId: activeUserId) { result in
                status = result
                showingSDK = false
            }
            .interactiveDismissDisabled()
        }
    }
}
