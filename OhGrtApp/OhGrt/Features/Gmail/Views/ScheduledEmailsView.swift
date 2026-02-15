import SwiftUI

/// View for managing scheduled emails
struct ScheduledEmailsView: View {
    @StateObject private var viewModel = DependencyContainer.shared.makeScheduledEmailsViewModel()
    @ObservedObject private var theme = ThemeManager.shared

    @State private var editingEmail: ScheduledEmail?
    @State private var showCancelConfirmation = false
    @State private var emailToCancel: ScheduledEmail?

    // Edit sheet fields
    @State private var editTo = ""
    @State private var editSubject = ""
    @State private var editBody = ""
    @State private var editScheduledDate = Date()

    var body: some View {
        NavigationStack {
            ZStack {
                Color(.systemBackground).ignoresSafeArea()

                if viewModel.isLoading && viewModel.scheduledEmails.isEmpty {
                    loadingView
                } else if viewModel.scheduledEmails.isEmpty && !viewModel.isLoading {
                    emptyStateView
                } else {
                    contentView
                }
            }
            .navigationTitle("Scheduled Emails")
            .navigationBarTitleDisplayMode(.large)
            .refreshable {
                await viewModel.loadEmails()
            }
            .task {
                await viewModel.loadEmails()
            }
            .sheet(item: $editingEmail) { email in
                editSheet(for: email)
            }
            .confirmationDialog(
                "Cancel Scheduled Email?",
                isPresented: $showCancelConfirmation,
                titleVisibility: .visible
            ) {
                Button("Cancel Email", role: .destructive) {
                    if let email = emailToCancel {
                        Task { await viewModel.cancelEmail(id: email.id) }
                    }
                }
                Button("Keep", role: .cancel) {}
            } message: {
                Text("This email will not be sent. This action cannot be undone.")
            }
        }
    }

    // MARK: - Content

    private var contentView: some View {
        ScrollView {
            VStack(spacing: 12) {
                // Stats bar
                statsBar
                    .padding(.horizontal, 16)

                // Filter
                filterPicker
                    .padding(.horizontal, 16)

                // Cards
                ForEach(viewModel.filteredEmails) { email in
                    ScheduledEmailCard(
                        email: email,
                        onEdit: {
                            editTo = email.to
                            editSubject = email.subject
                            editBody = email.body
                            if let date = parseDate(email.scheduledAt) {
                                editScheduledDate = date
                            }
                            editingEmail = email
                        },
                        onCancel: {
                            emailToCancel = email
                            showCancelConfirmation = true
                        }
                    )
                    .padding(.horizontal, 16)
                }

                Spacer(minLength: 40)
            }
            .padding(.top, 8)
        }
    }

    // MARK: - Stats Bar

    private var statsBar: some View {
        HStack(spacing: 16) {
            statItem(count: viewModel.activeCount, label: "Active", color: .blue)
            statItem(count: viewModel.completedCount, label: "Sent", color: .green)
            statItem(count: viewModel.cancelledCount, label: "Cancelled", color: .red)
            Spacer()
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.secondarySystemBackground))
        )
    }

    private func statItem(count: Int, label: String, color: Color) -> some View {
        VStack(spacing: 2) {
            Text("\(count)")
                .font(.headline)
                .fontWeight(.bold)
                .foregroundColor(color)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Filter Picker

    private var filterPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                filterChip(title: "All", status: nil)
                filterChip(title: "Scheduled", status: .active)
                filterChip(title: "Sent", status: .completed)
                filterChip(title: "Cancelled", status: .cancelled)
            }
        }
    }

    private func filterChip(title: String, status: ScheduledEmailStatus?) -> some View {
        Button {
            withAnimation(.spring(response: 0.3)) {
                viewModel.selectedStatus = status
            }
            Task { await viewModel.loadEmails() }
        } label: {
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(viewModel.selectedStatus == status ? .white : theme.primaryColor)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill(viewModel.selectedStatus == status ? theme.primaryColor : theme.primaryColor.opacity(0.12))
                )
        }
    }

    // MARK: - Edit Sheet

    private func editSheet(for email: ScheduledEmail) -> some View {
        NavigationStack {
            Form {
                Section("Recipient") {
                    TextField("To", text: $editTo)
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                }

                Section("Content") {
                    TextField("Subject", text: $editSubject)
                    TextEditor(text: $editBody)
                        .frame(minHeight: 100)
                }

                Section("Schedule") {
                    DatePicker(
                        "Send at",
                        selection: $editScheduledDate,
                        in: Date()...,
                        displayedComponents: [.date, .hourAndMinute]
                    )
                }
            }
            .navigationTitle("Edit Scheduled Email")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { editingEmail = nil }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        let formatter = ISO8601DateFormatter()
                        formatter.formatOptions = [.withInternetDateTime]
                        let dateString = formatter.string(from: editScheduledDate)

                        Task {
                            await viewModel.updateEmail(
                                id: email.id,
                                to: editTo,
                                subject: editSubject,
                                body: editBody,
                                scheduledAt: dateString
                            )
                            editingEmail = nil
                        }
                    }
                    .fontWeight(.semibold)
                }
            }
        }
    }

    // MARK: - Loading / Empty

    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.2)
            Text("Loading scheduled emails...")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "calendar.badge.clock")
                .font(.system(size: 56))
                .foregroundStyle(theme.primaryGradient)

            Text("No Scheduled Emails")
                .font(.title3)
                .fontWeight(.semibold)

            Text("Schedule emails from the compose screen to send them later.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }

    // MARK: - Helpers

    private func parseDate(_ dateStr: String) -> Date? {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: dateStr) { return date }
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.date(from: dateStr)
    }
}
