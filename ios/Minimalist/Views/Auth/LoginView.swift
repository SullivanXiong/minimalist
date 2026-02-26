import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authService: AuthService
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            Text("Minimalist")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(Theme.accentPurple)

            Spacer().frame(height: 32)

            VStack(spacing: 16) {
                TextField("Username", text: $username)
                    .textFieldStyle(.roundedBorder)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()

                SecureField("Password", text: $password)
                    .textFieldStyle(.roundedBorder)

                if let error = authService.error {
                    Text(error)
                        .foregroundColor(Theme.accentRed)
                        .font(.caption)
                }

                Button(action: {
                    isLoading = true
                    Task {
                        await authService.login(username: username, password: password)
                        isLoading = false
                    }
                }) {
                    if isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Sign In")
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(Theme.accentPurple)
                .disabled(username.isEmpty || password.isEmpty || isLoading)
            }
            .padding(.horizontal, 32)

            Spacer()
        }
        .background(Theme.bgPrimary)
    }
}
