import SwiftUI
import StoreKit

/// Modern paywall view shown when users try to access premium features
struct PaywallView: View {
    let feature: PremiumFeature?
    let onDismiss: () -> Void

    @StateObject private var manager = SubscriptionManager.shared
    @State private var selectedPlan: PlanType = .yearly
    @State private var isPurchasing = false
    @State private var showError = false
    @State private var errorMessage = ""

    // Animation states
    @State private var appeared = false
    @State private var plansAppeared = false
    @State private var shimmerOffset: CGFloat = -200

    enum PlanType {
        case monthly, yearly
    }

    init(feature: PremiumFeature? = nil, onDismiss: @escaping () -> Void) {
        self.feature = feature
        self.onDismiss = onDismiss
    }

    var body: some View {
        ZStack {
            // Background
            PaywallBackground()

            ScrollView(showsIndicators: false) {
                VStack(spacing: 24) {
                    // Close button
                    closeButton

                    // Header with feature highlight
                    headerSection

                    // Plan selection
                    planSelectionSection

                    // Feature comparison
                    featureComparisonSection

                    // CTA button
                    ctaButton

                    // Restore & Terms
                    footerSection

                    Spacer(minLength: 40)
                }
                .padding(.horizontal, 20)
            }
        }
        .onAppear {
            startAnimations()
            Task {
                await manager.loadProducts()
            }
        }
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }

    // MARK: - Close Button

    private var closeButton: some View {
        HStack {
            Spacer()
            Button(action: onDismiss) {
                Image(systemName: "xmark.circle.fill")
                    .font(.title2)
                    .foregroundColor(.white.opacity(0.5))
            }
        }
        .padding(.top, 16)
    }

    // MARK: - Header Section

    private var headerSection: some View {
        VStack(spacing: 20) {
            // Premium badge animation
            ZStack {
                ForEach(0..<3, id: \.self) { i in
                    Circle()
                        .stroke(
                            LinearGradient(
                                colors: [.orange.opacity(0.3), .pink.opacity(0.2)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 2
                        )
                        .frame(width: 70 + CGFloat(i * 20), height: 70 + CGFloat(i * 20))
                        .opacity(appeared ? 0.6 : 0)
                        .scaleEffect(appeared ? 1.1 : 0.8)
                        .animation(
                            .spring(response: 0.8, dampingFraction: 0.6)
                            .delay(Double(i) * 0.15),
                            value: appeared
                        )
                }

                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.orange, .pink],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 70, height: 70)
                        .shadow(color: .orange.opacity(0.5), radius: 15, y: 5)

                    Image(systemName: "crown.fill")
                        .font(.system(size: 32))
                        .foregroundColor(.white)
                }
            }
            .scaleEffect(appeared ? 1.0 : 0.8)
            .opacity(appeared ? 1.0 : 0)

            VStack(spacing: 8) {
                Text("Unlock Premium")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

                if let feature = feature {
                    Text("Get \(feature.displayName) and more!")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.7))
                } else {
                    Text("Access all features with one subscription")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.7))
                }
            }

            // Quick feature pills
            HStack(spacing: 8) {
                PaywallFeaturePill(icon: "infinity", text: "Unlimited")
                PaywallFeaturePill(icon: "bolt.fill", text: "Fast")
                PaywallFeaturePill(icon: "xmark.circle", text: "No Ads")
            }
        }
        .padding(.top, 20)
    }

    // MARK: - Plan Selection

    private var planSelectionSection: some View {
        VStack(spacing: 12) {
            // Yearly Plan (Recommended)
            PlanCard(
                title: "Yearly",
                subtitle: "Best Value",
                price: PricingConfig.yearlyPrice,
                perMonth: PricingConfig.yearlyMonthlyEquivalent,
                savings: PricingConfig.yearlySavings,
                isSelected: selectedPlan == .yearly,
                isPopular: true,
                shimmerOffset: shimmerOffset
            ) {
                withAnimation(.spring(response: 0.3)) {
                    selectedPlan = .yearly
                }
            }

            // Monthly Plan
            PlanCard(
                title: "Monthly",
                subtitle: "Flexible",
                price: PricingConfig.monthlyPrice,
                perMonth: nil,
                savings: nil,
                isSelected: selectedPlan == .monthly,
                isPopular: false,
                shimmerOffset: shimmerOffset
            ) {
                withAnimation(.spring(response: 0.3)) {
                    selectedPlan = .monthly
                }
            }
        }
        .opacity(plansAppeared ? 1 : 0)
        .offset(y: plansAppeared ? 0 : 20)
    }

    // MARK: - Feature Comparison

    private var featureComparisonSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("What you get")
                .font(.headline)
                .foregroundColor(.white)

            VStack(spacing: 12) {
                ComparisonRow(icon: "bubble.left.and.bubble.right.fill", text: "Unlimited AI Messages", included: true)
                ComparisonRow(icon: "sparkles", text: "All Astrology Features", included: true)
                ComparisonRow(icon: "train.side.front.car", text: "Advanced Train Tracking", included: true)
                ComparisonRow(icon: "wand.and.stars", text: "AI Image Generation", included: selectedPlan == .yearly)
                ComparisonRow(icon: "bolt.fill", text: "Priority Response", included: selectedPlan == .yearly)
                ComparisonRow(icon: "xmark.circle.fill", text: "Ad-Free Experience", included: true)
            }
        }
        .padding(16)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }

    // MARK: - CTA Button

    private var ctaButton: some View {
        Button {
            Task {
                await purchaseSelectedPlan()
            }
        } label: {
            HStack(spacing: 10) {
                if isPurchasing {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Image(systemName: "crown.fill")
                        .font(.headline)
                    Text("Continue with \(selectedPlan == .yearly ? "Pro" : "Plus")")
                        .font(.headline)
                        .fontWeight(.bold)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .background(
                ZStack {
                    LinearGradient(
                        colors: selectedPlan == .yearly ?
                            [.orange, .pink] : [.blue, .purple],
                        startPoint: .leading,
                        endPoint: .trailing
                    )

                    // Shimmer
                    LinearGradient(
                        colors: [.clear, .white.opacity(0.3), .clear],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                    .offset(x: shimmerOffset)
                }
            )
            .foregroundColor(.white)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .shadow(color: (selectedPlan == .yearly ? Color.orange : Color.purple).opacity(0.4), radius: 10, y: 5)
        }
        .disabled(isPurchasing || manager.products.isEmpty)
    }

    // MARK: - Footer

    private var footerSection: some View {
        VStack(spacing: 16) {
            // Restore purchases
            Button {
                Task {
                    await manager.restorePurchases()
                }
            } label: {
                Text("Restore Purchases")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.6))
            }
            .disabled(manager.isLoading)

            // Terms
            Text("Cancel anytime. Subscription auto-renews unless cancelled 24 hours before the end of the current period.")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.4))
                .multilineTextAlignment(.center)

            // Links
            HStack(spacing: 20) {
                Link("Privacy", destination: URL(string: "https://ohgrt.com/privacy")!)
                Link("Terms", destination: URL(string: "https://ohgrt.com/terms")!)
            }
            .font(.caption)
            .foregroundColor(.white.opacity(0.5))
        }
    }

    // MARK: - Actions

    private func purchaseSelectedPlan() async {
        isPurchasing = true
        defer { isPurchasing = false }

        let productId = selectedPlan == .yearly ?
            PricingConfig.yearlyProductId : PricingConfig.monthlyProductId

        guard let product = manager.products.first(where: { $0.id == productId }) else {
            errorMessage = "Product not available"
            showError = true
            return
        }

        do {
            let success = try await manager.purchase(product)
            if success {
                let feedback = UINotificationFeedbackGenerator()
                feedback.notificationOccurred(.success)
                onDismiss()
            }
        } catch {
            errorMessage = "Purchase failed: \(error.localizedDescription)"
            showError = true
        }
    }

    private func startAnimations() {
        withAnimation(.spring(response: 0.6, dampingFraction: 0.7).delay(0.1)) {
            appeared = true
        }

        withAnimation(.spring(response: 0.5, dampingFraction: 0.7).delay(0.3)) {
            plansAppeared = true
        }

        // Single shimmer sweep animation
        withAnimation(.easeInOut(duration: 1.5).delay(0.5)) {
            shimmerOffset = 400
        }
    }
}

// MARK: - Supporting Views

private struct PaywallFeaturePill: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2)
            Text(text)
                .font(.caption2)
                .fontWeight(.medium)
        }
        .foregroundColor(.white)
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(Color.white.opacity(0.15))
        .clipShape(Capsule())
    }
}

private struct PlanCard: View {
    let title: String
    let subtitle: String
    let price: String
    let perMonth: String?
    let savings: String?
    let isSelected: Bool
    let isPopular: Bool
    let shimmerOffset: CGFloat
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack {
                // Radio button
                ZStack {
                    Circle()
                        .stroke(isSelected ? Color.orange : Color.white.opacity(0.3), lineWidth: 2)
                        .frame(width: 24, height: 24)

                    if isSelected {
                        Circle()
                            .fill(Color.orange)
                            .frame(width: 14, height: 14)
                    }
                }

                VStack(alignment: .leading, spacing: 2) {
                    HStack(spacing: 8) {
                        Text(title)
                            .font(.headline)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)

                        if isPopular {
                            Text("BEST VALUE")
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 3)
                                .background(
                                    LinearGradient(
                                        colors: [.orange, .pink],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .clipShape(Capsule())
                        }
                    }

                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.5))
                }

                Spacer()

                VStack(alignment: .trailing, spacing: 2) {
                    Text(price)
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.white)

                    if let perMonth = perMonth {
                        Text(perMonth)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.5))
                    }

                    if let savings = savings {
                        Text(savings)
                            .font(.caption2)
                            .fontWeight(.semibold)
                            .foregroundColor(.green)
                    }
                }
            }
            .padding(16)
            .background(
                ZStack {
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.white.opacity(isSelected ? 0.1 : 0.05))

                    if isSelected && isPopular {
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(
                                LinearGradient(
                                    colors: [.orange, .pink],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                ),
                                lineWidth: 2
                            )
                    } else if isSelected {
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.blue, lineWidth: 2)
                    }
                }
            )
        }
        .buttonStyle(.plain)
    }
}

private struct ComparisonRow: View {
    let icon: String
    let text: String
    let included: Bool

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.subheadline)
                .foregroundColor(included ? .orange : .white.opacity(0.3))
                .frame(width: 24)

            Text(text)
                .font(.subheadline)
                .foregroundColor(included ? .white : .white.opacity(0.4))

            Spacer()

            Image(systemName: included ? "checkmark.circle.fill" : "xmark.circle")
                .font(.subheadline)
                .foregroundColor(included ? .green : .white.opacity(0.3))
        }
    }
}

private struct PaywallBackground: View {
    @State private var animate = false

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            // Gradient mesh
            LinearGradient(
                colors: [
                    Color.orange.opacity(0.15),
                    Color.purple.opacity(0.1),
                    Color.pink.opacity(0.08),
                    Color.black
                ],
                startPoint: animate ? .topLeading : .topTrailing,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            // Floating orbs - single entry animation
            GeometryReader { geo in
                ZStack {
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [.orange.opacity(0.2), .clear],
                                center: .center,
                                startRadius: 0,
                                endRadius: 150
                            )
                        )
                        .frame(width: 300, height: 300)
                        .offset(x: -50, y: animate ? -20 : 20)
                        .blur(radius: 60)
                        .opacity(animate ? 1 : 0)

                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [.pink.opacity(0.15), .clear],
                                center: .center,
                                startRadius: 0,
                                endRadius: 100
                            )
                        )
                        .frame(width: 200, height: 200)
                        .offset(x: geo.size.width - 100, y: geo.size.height - (animate ? 170 : 200))
                        .blur(radius: 50)
                        .opacity(animate ? 1 : 0)
                }
            }
            .ignoresSafeArea()
        }
        .onAppear {
            // Single gentle entry animation
            withAnimation(.easeOut(duration: 1.5)) {
                animate = true
            }
        }
    }
}

// MARK: - Mini Paywall (for inline use)

struct MiniPaywall: View {
    let feature: PremiumFeature
    let onUpgrade: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            HStack(spacing: 12) {
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.orange.opacity(0.2), .pink.opacity(0.1)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 50, height: 50)

                    Image(systemName: "lock.fill")
                        .font(.title3)
                        .foregroundColor(.orange)
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text("Premium Feature")
                        .font(.headline)
                        .foregroundColor(.white)

                    Text("\(feature.displayName) requires \(feature.minimumTier.displayName)")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.6))
                }

                Spacer()
            }

            Button(action: onUpgrade) {
                HStack(spacing: 8) {
                    Image(systemName: "crown.fill")
                        .font(.subheadline)
                    Text("Upgrade to \(feature.minimumTier.displayName)")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(
                    LinearGradient(
                        colors: feature.minimumTier == .pro ?
                            [.orange, .pink] : [.blue, .purple],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .foregroundColor(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
        }
        .padding(16)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.orange.opacity(0.3), lineWidth: 1)
        )
    }
}

// MARK: - Usage Limit Banner

struct UsageLimitBanner: View {
    let remainingCount: Int
    let totalCount: Int
    let featureName: String
    let onUpgrade: () -> Void

    private var progress: Double {
        guard totalCount > 0 else { return 0 }
        return Double(totalCount - remainingCount) / Double(totalCount)
    }

    private var isLow: Bool {
        remainingCount <= 2
    }

    var body: some View {
        VStack(spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(remainingCount) \(featureName) left today")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(isLow ? .orange : .white)

                    Text("Upgrade for unlimited access")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.5))
                }

                Spacer()

                Button(action: onUpgrade) {
                    Text("Upgrade")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 8)
                        .background(
                            LinearGradient(
                                colors: [.orange, .pink],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .clipShape(Capsule())
                }
            }

            // Progress bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.white.opacity(0.1))

                    RoundedRectangle(cornerRadius: 4)
                        .fill(
                            LinearGradient(
                                colors: isLow ?
                                    [.orange, .red] : [.green, .cyan],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: geo.size.width * progress)
                }
            }
            .frame(height: 6)
        }
        .padding(14)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}

// MARK: - Preview

#Preview("Paywall") {
    PaywallView(feature: .aiImageGeneration) {}
}

#Preview("Mini Paywall") {
    VStack {
        MiniPaywall(feature: .aiImageGeneration) {}
            .padding()
    }
    .background(Color.black)
}

#Preview("Usage Limit") {
    VStack {
        UsageLimitBanner(
            remainingCount: 3,
            totalCount: 10,
            featureName: "messages",
            onUpgrade: {}
        )
        .padding()

        UsageLimitBanner(
            remainingCount: 1,
            totalCount: 10,
            featureName: "messages",
            onUpgrade: {}
        )
        .padding()
    }
    .background(Color.black)
}
