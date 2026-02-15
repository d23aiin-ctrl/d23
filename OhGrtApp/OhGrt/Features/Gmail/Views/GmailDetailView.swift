import SwiftUI

/// Detail view for a single Gmail message
struct GmailDetailView: View {
    @ObservedObject var viewModel: GmailViewModel
    let messageId: String
    let subject: String

    @ObservedObject private var theme = ThemeManager.shared
    @State private var htmlHeight: CGFloat = 100
    @State private var showReply = false
    @State private var appeared = false

    var body: some View {
        Group {
            if viewModel.isLoadingDetail {
                loadingView
            } else if let detail = viewModel.selectedEmail {
                emailContent(detail)
            } else {
                errorView
            }
        }
        .navigationTitle(subject)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItemGroup(placement: .navigationBarTrailing) {
                Button {
                    showReply = true
                } label: {
                    Image(systemName: "arrowshape.turn.up.left.fill")
                        .font(.system(size: 16))
                }

                Button {
                    showReply = true
                } label: {
                    Image(systemName: "arrowshape.turn.up.right.fill")
                        .font(.system(size: 16))
                }
            }
        }
        .task {
            await viewModel.getEmailDetail(id: messageId)
        }
        .sheet(isPresented: $showReply) {
            if let detail = viewModel.selectedEmail {
                ComposeEmailView(
                    viewModel: viewModel,
                    replyTo: detail.from,
                    replySubject: detail.subject.hasPrefix("Re:") ? detail.subject : "Re: \(detail.subject)"
                )
            }
        }
    }

    // MARK: - Email Content

    private func emailContent(_ detail: GmailMessageDetail) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Subject
                Text(detail.subject)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                    .padding(.horizontal, 16)
                    .padding(.top, 16)

                // Metadata card
                metadataCard(detail)
                    .padding(.horizontal, 16)

                Divider()
                    .padding(.horizontal, 16)

                // Body
                if isHTML(detail.body) {
                    HTMLBodyView(htmlContent: detail.body, dynamicHeight: $htmlHeight)
                        .frame(height: htmlHeight)
                        .padding(.horizontal, 8)
                } else {
                    Text(detail.body)
                        .font(.body)
                        .foregroundColor(.primary)
                        .textSelection(.enabled)
                        .padding(.horizontal, 16)
                }

                Spacer(minLength: 40)
            }
            .opacity(appeared ? 1 : 0)
            .offset(y: appeared ? 0 : 10)
            .onAppear {
                withAnimation(.easeOut(duration: 0.3)) {
                    appeared = true
                }
            }
        }
    }

    // MARK: - Metadata

    private func metadataCard(_ detail: GmailMessageDetail) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            metadataRow(label: "From", value: detail.from)
            metadataRow(label: "To", value: detail.to)

            if let cc = detail.cc, !cc.isEmpty {
                metadataRow(label: "CC", value: cc)
            }

            metadataRow(label: "Date", value: detail.date)
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.secondarySystemBackground))
        )
    }

    private func metadataRow(label: String, value: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Text(label)
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.secondary)
                .frame(width: 40, alignment: .trailing)

            Text(value)
                .font(.caption)
                .foregroundColor(.primary)
                .textSelection(.enabled)
        }
    }

    // MARK: - Loading / Error

    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.2)
            Text("Loading email...")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var errorView: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 40))
                .foregroundColor(.orange)

            Text("Could not load email")
                .font(.subheadline)
                .foregroundColor(.secondary)

            Button("Retry") {
                Task { await viewModel.getEmailDetail(id: messageId) }
            }
            .font(.subheadline)
            .fontWeight(.medium)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - Helpers

    private func isHTML(_ text: String) -> Bool {
        text.contains("<") && text.contains(">") &&
        (text.contains("<div") || text.contains("<p") || text.contains("<br") ||
         text.contains("<html") || text.contains("<table") || text.contains("<span"))
    }
}
