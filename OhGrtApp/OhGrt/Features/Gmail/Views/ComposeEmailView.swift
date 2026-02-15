import SwiftUI

/// Compose or schedule an email
struct ComposeEmailView: View {
    @ObservedObject var viewModel: GmailViewModel
    @ObservedObject private var theme = ThemeManager.shared
    @Environment(\.dismiss) private var dismiss

    // Pre-fill for reply
    var replyTo: String = ""
    var replySubject: String = ""

    // Form fields
    @State private var toField = ""
    @State private var subjectField = ""
    @State private var bodyField = ""
    @State private var ccField = ""
    @State private var bccField = ""
    @State private var showCcBcc = false

    // Scheduling
    @State private var isScheduled = false
    @State private var scheduledDate = Date().addingTimeInterval(3600)
    @State private var showDatePicker = false

    // Validation
    @State private var validationError: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    // To field
                    fieldRow(label: "To", text: $toField, placeholder: "recipient@example.com")

                    // CC/BCC toggle
                    if showCcBcc {
                        fieldRow(label: "CC", text: $ccField, placeholder: "cc@example.com")
                        fieldRow(label: "BCC", text: $bccField, placeholder: "bcc@example.com")
                    }

                    Button {
                        withAnimation(.spring(response: 0.3)) {
                            showCcBcc.toggle()
                        }
                    } label: {
                        HStack {
                            Image(systemName: showCcBcc ? "chevron.up" : "chevron.down")
                                .font(.system(size: 12))
                            Text(showCcBcc ? "Hide CC/BCC" : "Show CC/BCC")
                                .font(.caption)
                        }
                        .foregroundColor(theme.primaryColor)
                    }
                    .padding(.horizontal, 16)
                    .frame(maxWidth: .infinity, alignment: .leading)

                    // Subject field
                    fieldRow(label: "Subject", text: $subjectField, placeholder: "Email subject")

                    // Body
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Body")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.secondary)

                        TextEditor(text: $bodyField)
                            .frame(minHeight: 200)
                            .padding(10)
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(Color(.secondarySystemBackground))
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(Color(.systemGray4), lineWidth: 1)
                            )
                    }
                    .padding(.horizontal, 16)

                    Divider()
                        .padding(.horizontal, 16)

                    // Schedule toggle
                    scheduleSection

                    // Validation error
                    if let error = validationError {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 16)
                    }

                    // Send/Schedule error from VM
                    if let error = viewModel.error {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 16)
                    }

                    Spacer(minLength: 40)
                }
                .padding(.top, 16)
            }
            .navigationTitle(isScheduled ? "Schedule Email" : "Compose")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        Task { await send() }
                    } label: {
                        if viewModel.isSending {
                            ProgressView()
                                .tint(.white)
                        } else {
                            HStack(spacing: 4) {
                                Image(systemName: isScheduled ? "clock.fill" : "paperplane.fill")
                                Text(isScheduled ? "Schedule" : "Send")
                            }
                            .font(.subheadline)
                            .fontWeight(.semibold)
                        }
                    }
                    .disabled(viewModel.isSending)
                }
            }
            .onAppear {
                if !replyTo.isEmpty { toField = replyTo }
                if !replySubject.isEmpty { subjectField = replySubject }
            }
            .onChange(of: viewModel.sendSuccess) { _, success in
                if success {
                    dismiss()
                }
            }
        }
    }

    // MARK: - Field Row

    private func fieldRow(label: String, text: Binding<String>, placeholder: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label)
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.secondary)

            TextField(placeholder, text: text)
                .textFieldStyle(.plain)
                .font(.body)
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color(.secondarySystemBackground))
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color(.systemGray4), lineWidth: 1)
                )
                .autocapitalization(.none)
                .keyboardType(label == "Subject" ? .default : .emailAddress)
                .textContentType(label == "Subject" ? nil : .emailAddress)
        }
        .padding(.horizontal, 16)
    }

    // MARK: - Schedule Section

    private var scheduleSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Toggle(isOn: $isScheduled.animation(.spring(response: 0.3))) {
                HStack(spacing: 8) {
                    Image(systemName: "clock.fill")
                        .foregroundStyle(theme.primaryGradient)
                    Text("Schedule for later")
                        .font(.subheadline)
                        .fontWeight(.medium)
                }
            }
            .tint(theme.primaryColor)
            .padding(.horizontal, 16)

            if isScheduled {
                // Quick presets
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        presetButton("10 min", offset: 10 * 60)
                        presetButton("30 min", offset: 30 * 60)
                        presetButton("1 hour", offset: 60 * 60)
                        presetButton("2 hours", offset: 2 * 60 * 60)
                        presetButton("Tomorrow 9 AM", offset: nil)
                    }
                    .padding(.horizontal, 16)
                }

                // Custom picker
                Button {
                    withAnimation { showDatePicker.toggle() }
                } label: {
                    HStack {
                        Image(systemName: "calendar")
                        Text(formattedScheduleDate)
                            .font(.subheadline)
                        Spacer()
                        Image(systemName: showDatePicker ? "chevron.up" : "chevron.down")
                            .font(.system(size: 12))
                    }
                    .foregroundColor(.primary)
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color(.secondarySystemBackground))
                    )
                }
                .padding(.horizontal, 16)

                if showDatePicker {
                    DatePicker(
                        "Schedule",
                        selection: $scheduledDate,
                        in: Date()...,
                        displayedComponents: [.date, .hourAndMinute]
                    )
                    .datePickerStyle(.graphical)
                    .padding(.horizontal, 16)
                }
            }
        }
    }

    private func presetButton(_ title: String, offset: TimeInterval?) -> some View {
        Button {
            if let offset = offset {
                scheduledDate = Date().addingTimeInterval(offset)
            } else {
                // Tomorrow 9 AM
                let calendar = Calendar.current
                if let tomorrow = calendar.date(byAdding: .day, value: 1, to: Date()) {
                    scheduledDate = calendar.date(bySettingHour: 9, minute: 0, second: 0, of: tomorrow) ?? tomorrow
                }
            }
        } label: {
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(theme.primaryColor)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill(theme.primaryColor.opacity(0.12))
                )
                .overlay(
                    Capsule()
                        .stroke(theme.primaryColor.opacity(0.3), lineWidth: 1)
                )
        }
    }

    private var formattedScheduleDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: scheduledDate)
    }

    // MARK: - Send

    private func send() async {
        validationError = nil

        // Validate
        guard !toField.trimmingCharacters(in: .whitespaces).isEmpty else {
            validationError = "Recipient email is required."
            return
        }

        let emailRegex = #"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"#
        let emails = toField.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }
        for email in emails {
            if email.range(of: emailRegex, options: .regularExpression) == nil {
                validationError = "Invalid email: \(email)"
                return
            }
        }

        guard !subjectField.trimmingCharacters(in: .whitespaces).isEmpty else {
            validationError = "Subject is required."
            return
        }

        let cc = ccField.isEmpty ? nil : ccField
        let bcc = bccField.isEmpty ? nil : bccField

        if isScheduled {
            await viewModel.scheduleEmail(
                to: toField,
                subject: subjectField,
                body: bodyField,
                cc: cc,
                bcc: bcc,
                scheduledAt: scheduledDate
            )
        } else {
            await viewModel.sendEmail(
                to: toField,
                subject: subjectField,
                body: bodyField,
                cc: cc,
                bcc: bcc
            )
        }
    }
}
