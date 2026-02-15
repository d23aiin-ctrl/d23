import SwiftUI

/// Gmail inbox view with search, pull-to-refresh, and compose
struct GmailInboxView: View {
    @ObservedObject var viewModel: GmailViewModel
    @ObservedObject private var theme = ThemeManager.shared

    @State private var showCompose = false
    @State private var navigateToDetail: GmailMessageSummary?

    var body: some View {
        NavigationStack {
            ZStack {
                Color(.systemBackground).ignoresSafeArea()

                if viewModel.isLoading && viewModel.emails.isEmpty {
                    loadingView
                } else if viewModel.emails.isEmpty && !viewModel.isLoading {
                    emptyStateView
                } else {
                    emailListView
                }

                // FAB Compose Button
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        composeButton
                    }
                }
                .padding(20)
            }
            .navigationTitle("Gmail")
            .navigationBarTitleDisplayMode(.large)
            .searchable(text: $viewModel.searchText, prompt: "Search emails...")
            .onSubmit(of: .search) {
                Task {
                    await viewModel.searchEmails()
                }
            }
            .refreshable {
                await viewModel.loadInbox()
            }
            .task {
                if viewModel.emails.isEmpty {
                    await viewModel.loadInbox()
                }
            }
            .sheet(isPresented: $showCompose) {
                ComposeEmailView(viewModel: viewModel)
            }
            .navigationDestination(item: $navigateToDetail) { message in
                GmailDetailView(viewModel: viewModel, messageId: message.id, subject: message.subject)
            }
            .alert("Error", isPresented: .init(
                get: { viewModel.error != nil },
                set: { if !$0 { viewModel.error = nil } }
            )) {
                Button("OK") { viewModel.error = nil }
            } message: {
                Text(viewModel.error ?? "")
            }
        }
    }

    // MARK: - Email List

    private var emailListView: some View {
        ScrollView {
            LazyVStack(spacing: 8) {
                // Stats bar
                statsBar
                    .padding(.horizontal, 16)
                    .padding(.top, 8)

                ForEach(Array(viewModel.filteredEmails.enumerated()), id: \.element.id) { index, email in
                    GmailMessageRow(message: email, index: index)
                        .padding(.horizontal, 16)
                        .onTapGesture {
                            navigateToDetail = email
                        }
                }
            }
            .padding(.bottom, 80)
        }
    }

    // MARK: - Stats Bar

    private var statsBar: some View {
        HStack(spacing: 16) {
            HStack(spacing: 6) {
                Image(systemName: "envelope.fill")
                    .font(.system(size: 14))
                    .foregroundStyle(theme.primaryGradient)
                Text("\(viewModel.filteredEmails.count) emails")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
            }

            Spacer()

            if !viewModel.searchText.isEmpty {
                HStack(spacing: 4) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 12))
                    Text("Filtered")
                        .font(.caption)
                }
                .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }

    // MARK: - Loading

    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.2)
            Text("Loading emails...")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Empty State

    private var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "envelope.open")
                .font(.system(size: 56))
                .foregroundStyle(theme.primaryGradient)

            Text("No Emails")
                .font(.title3)
                .fontWeight(.semibold)

            Text("Your inbox is empty or no results match your search.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button {
                Task { await viewModel.loadInbox() }
            } label: {
                Text("Refresh")
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 10)
                    .background(theme.primaryGradient)
                    .clipShape(Capsule())
            }
        }
    }

    // MARK: - Compose FAB

    private var composeButton: some View {
        Button {
            showCompose = true
        } label: {
            Image(systemName: "square.and.pencil")
                .font(.system(size: 22, weight: .semibold))
                .foregroundColor(.white)
                .frame(width: 56, height: 56)
                .background(theme.primaryGradient)
                .clipShape(Circle())
                .shadow(color: theme.primaryColor.opacity(0.4), radius: 10, y: 5)
        }
    }
}
