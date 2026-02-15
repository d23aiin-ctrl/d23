import SwiftUI

/// Super App Home Screen with Service Grid
struct SuperAppHomeView: View {
    @State private var searchText = ""
    @State private var showChat = false
    @State private var chatPrefill: String?
    @State private var selectedService: AppService?
    @State private var showAllServices = false
    @State private var greeting = "Hello"
    @State private var showPaywall = false
    @State private var showSubscription = false

    // Animation states for staggered entry
    @State private var animateHeader = false
    @State private var animateSearch = false
    @State private var animateQuickActions = false
    @State private var animatePremiumBanner = false
    @State private var animateServices = false
    @State private var animateAIBanner = false
    @State private var animateMoreServices = false
    @State private var animateRecentActivity = false

    @EnvironmentObject var authManager: AuthManager
    @StateObject private var subscriptionManager = SubscriptionManager.shared

    // Quick actions for top section
    let quickActions: [QuickAction] = [
        QuickAction(icon: "bubble.left.and.bubble.right.fill", title: "Ask AI", color: .purple, action: "chat"),
        QuickAction(icon: "magnifyingglass", title: "Search", color: .blue, action: "search"),
        QuickAction(icon: "mic.fill", title: "Voice", color: .green, action: "voice"),
        QuickAction(icon: "camera.fill", title: "Scan", color: .orange, action: "scan"),
    ]

    // Main services grid
    let mainServices: [AppService] = [
        AppService(id: "astrology", name: "Astrology", icon: "sparkles", color: .orange, gradient: [.orange, .red], subtitle: "Horoscope & Kundli"),
        AppService(id: "news", name: "News", icon: "newspaper.fill", color: .red, gradient: [.red, .pink], subtitle: "Latest Headlines"),
        AppService(id: "weather", name: "Weather", icon: "cloud.sun.fill", color: .cyan, gradient: [.cyan, .blue], subtitle: "Live Forecast"),
        AppService(id: "travel", name: "Travel", icon: "tram.fill", color: .blue, gradient: [.blue, .indigo], subtitle: "PNR & Trains"),
        AppService(id: "jobs", name: "Govt Jobs", icon: "briefcase.fill", color: .green, gradient: [.green, .mint], subtitle: "Sarkari Naukri"),
        AppService(id: "cricket", name: "Cricket", icon: "sportscourt.fill", color: .mint, gradient: [.mint, .green], subtitle: "Live Scores"),
        AppService(id: "images", name: "AI Images", icon: "wand.and.stars", color: .pink, gradient: [.pink, .purple], subtitle: "Generate Art"),
        AppService(id: "stocks", name: "Stocks", icon: "chart.line.uptrend.xyaxis", color: .green, gradient: [.green, .teal], subtitle: "Market Watch"),
    ]

    // More services
    let moreServices: [AppService] = [
        AppService(id: "food", name: "Food", icon: "fork.knife", color: .orange, gradient: [.orange, .yellow], subtitle: "Nearby Places"),
        AppService(id: "reminder", name: "Reminders", icon: "bell.fill", color: .yellow, gradient: [.yellow, .orange], subtitle: "Never Forget"),
        AppService(id: "translate", name: "Translate", icon: "character.bubble.fill", color: .indigo, gradient: [.indigo, .purple], subtitle: "22+ Languages"),
        AppService(id: "calculator", name: "Calculator", icon: "function", color: .gray, gradient: [.gray, .black], subtitle: "Quick Math"),
        AppService(id: "facts", name: "Fact Check", icon: "checkmark.shield.fill", color: .blue, gradient: [.blue, .cyan], subtitle: "Verify Info"),
        AppService(id: "games", name: "Games", icon: "gamecontroller.fill", color: .purple, gradient: [.purple, .pink], subtitle: "Word Games"),
    ]

    var body: some View {
        NavigationStack {
            ZStack {
                // Background
                SuperAppBackground()

                ScrollView(showsIndicators: false) {
                    VStack(spacing: 24) {
                        // Header with greeting
                        headerSection
                            .opacity(animateHeader ? 1 : 0)
                            .offset(y: animateHeader ? 0 : -20)

                        // Search Bar
                        searchBar
                            .opacity(animateSearch ? 1 : 0)
                            .scaleEffect(animateSearch ? 1 : 0.95)

                        // Quick Actions
                        quickActionsRow
                            .opacity(animateQuickActions ? 1 : 0)
                            .offset(y: animateQuickActions ? 0 : 15)

                        // Premium Upgrade Banner (for free users)
                        premiumUpgradeBanner
                            .opacity(animatePremiumBanner ? 1 : 0)
                            .offset(x: animatePremiumBanner ? 0 : -30)

                        // Main Services Grid
                        mainServicesSection
                            .opacity(animateServices ? 1 : 0)

                        // AI Chat Banner
                        aiChatBanner
                            .opacity(animateAIBanner ? 1 : 0)
                            .scaleEffect(animateAIBanner ? 1 : 0.9)

                        // More Services
                        moreServicesSection
                            .opacity(animateMoreServices ? 1 : 0)
                            .offset(y: animateMoreServices ? 0 : 20)

                        // Recent Activity
                        recentActivitySection
                            .opacity(animateRecentActivity ? 1 : 0)
                            .offset(y: animateRecentActivity ? 0 : 20)

                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, 16)
                }
            }
            .navigationBarHidden(true)
            .fullScreenCover(isPresented: $showChat) {
                NavigationStack {
                    ChatView(conversationId: nil, showWelcomeOnEmpty: false, initialPrompt: chatPrefill)
                }
            }
            .fullScreenCover(isPresented: $showPaywall) {
                PaywallView {
                    showPaywall = false
                }
            }
            .sheet(isPresented: $showSubscription) {
                SubscriptionView()
            }
            .sheet(item: $selectedService) { service in
                ServiceDetailSheet(service: service, onOpenChat: {
                    chatPrefill = servicePrompt(for: service)
                    showChat = true
                }, onUpgrade: {
                    showPaywall = true
                })
            }
        }
        .onAppear {
            updateGreeting()
            triggerEntryAnimations()
        }
        .onChange(of: showChat) { _, isShowing in
            if !isShowing {
                chatPrefill = nil
            }
        }
    }

    // MARK: - Header Section

    private var headerSection: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 8) {
                    Text(greeting)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)

                    // Premium Badge
                    if subscriptionManager.isPremium {
                        Text(subscriptionManager.currentTier.badge)
                            .font(.system(size: 10, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(
                                LinearGradient(
                                    colors: subscriptionManager.currentTier.badgeGradient,
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .clipShape(Capsule())
                    }
                }

                Text("What would you like to do today?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            Spacer()

            // Profile Button with Premium indicator
            Button(action: { showSubscription = true }) {
                ZStack(alignment: .bottomTrailing) {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: subscriptionManager.isPremium ?
                                    subscriptionManager.currentTier.badgeGradient :
                                    [.purple, .blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 44, height: 44)

                    Image(systemName: subscriptionManager.isPremium ?
                          subscriptionManager.currentTier.icon : "person.fill")
                        .font(.system(size: 18))
                        .foregroundColor(.white)

                    // Crown badge for premium
                    if subscriptionManager.isPremium {
                        Circle()
                            .fill(Color.black)
                            .frame(width: 18, height: 18)
                            .overlay(
                                Image(systemName: "checkmark")
                                    .font(.system(size: 10, weight: .bold))
                                    .foregroundColor(.green)
                            )
                            .offset(x: 2, y: 2)
                    }
                }
            }
        }
        .padding(.top, 60)
    }

    // MARK: - Search Bar

    private var searchBar: some View {
        Button(action: { showChat = true }) {
            HStack(spacing: 12) {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 18))
                    .foregroundColor(.secondary)

                Text("Ask anything...")
                    .font(.body)
                    .foregroundColor(.secondary)

                Spacer()

                Image(systemName: "mic.fill")
                    .font(.system(size: 16))
                    .foregroundColor(.purple)
                    .padding(8)
                    .background(Color.purple.opacity(0.2))
                    .clipShape(Circle())
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .background(Color(.systemGray6))
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color(.systemGray4), lineWidth: 1)
            )
        }
    }

    // MARK: - Quick Actions

    private var quickActionsRow: some View {
        HStack(spacing: 0) {
            ForEach(Array(quickActions.enumerated()), id: \.element.title) { index, action in
                QuickActionButton(action: action, index: index) {
                    if action.action == "chat" {
                        showChat = true
                    }
                }
            }
        }
        .padding(.vertical, 12)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }

    // MARK: - Main Services

    private var mainServicesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Services")
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)

                Spacer()

                Button(action: { showAllServices.toggle() }) {
                    Text("See All")
                        .font(.subheadline)
                        .foregroundColor(.purple)
                }
            }

            LazyVGrid(columns: [
                GridItem(.flexible(), spacing: 8),
                GridItem(.flexible(), spacing: 8),
                GridItem(.flexible(), spacing: 8),
                GridItem(.flexible(), spacing: 8)
            ], spacing: 12) {
                ForEach(mainServices.indices, id: \.self) { index in
                    ServiceGridItem(service: mainServices[index], index: index)
                        .opacity(animateServices ? 1 : 0)
                        .offset(y: animateServices ? 0 : 20)
                        .animation(
                            .spring(response: 0.5, dampingFraction: 0.7)
                            .delay(Double(index) * 0.06),
                            value: animateServices
                        )
                        .onTapGesture {
                            handleServiceTap(mainServices[index])
                        }
                }
            }
            .padding(.horizontal, -4)
        }
    }

    // MARK: - Premium Upgrade Banner (for free users)

    @ViewBuilder
    private var premiumUpgradeBanner: some View {
        if !subscriptionManager.isPremium {
            Button(action: { showPaywall = true }) {
                HStack(spacing: 14) {
                    ZStack {
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: [.orange, .pink],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .frame(width: 50, height: 50)

                        Image(systemName: "crown.fill")
                            .font(.system(size: 22))
                            .foregroundColor(.white)
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Upgrade to Premium")
                            .font(.headline)
                            .foregroundColor(.primary)

                        Text("Unlock unlimited AI, astrology & more")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    VStack(spacing: 2) {
                        Text("From")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text(PricingConfig.yearlyMonthlyEquivalent)
                            .font(.subheadline)
                            .fontWeight(.bold)
                            .foregroundColor(.orange)
                    }
                }
                .padding(16)
                .background(
                    LinearGradient(
                        colors: [Color.orange.opacity(0.2), Color.pink.opacity(0.15)],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .clipShape(RoundedRectangle(cornerRadius: 20))
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(
                            LinearGradient(
                                colors: [.orange.opacity(0.5), .pink.opacity(0.3)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 1
                        )
                )
            }
        }
    }

    // MARK: - AI Chat Banner

    private var aiChatBanner: some View {
        Button(action: { showChat = true }) {
            HStack(spacing: 16) {
                // AI Avatar with animation
                ZStack {
                    // Glow effect
                    Circle()
                        .fill(Color.purple.opacity(0.3))
                        .frame(width: 64, height: 64)
                        .scaleEffect(animateAIBanner ? 1.0 : 0.5)
                        .opacity(animateAIBanner ? 0.6 : 0)
                        .blur(radius: 6)

                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.purple, .blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 56, height: 56)
                        .scaleEffect(animateAIBanner ? 1.0 : 0.7)

                    Image(systemName: "sparkles")
                        .font(.system(size: 24))
                        .foregroundColor(.white)
                        .scaleEffect(animateAIBanner ? 1.0 : 0.5)
                        .rotationEffect(.degrees(animateAIBanner ? 0 : -20))
                }

                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 6) {
                        Text("D23 AI Assistant")
                            .font(.headline)
                            .foregroundColor(.primary)

                        if subscriptionManager.isPremium {
                            Text(subscriptionManager.currentTier.badge)
                                .font(.system(size: 8, weight: .bold))
                                .foregroundColor(.white)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(
                                    LinearGradient(
                                        colors: subscriptionManager.currentTier.badgeGradient,
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .clipShape(Capsule())
                        }
                    }

                    Text(subscriptionManager.isPremium ?
                         "Unlimited messages • Priority responses" :
                         "Ask me anything in 22+ languages")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)
            }
            .padding(16)
            .background(
                LinearGradient(
                    colors: [Color.purple.opacity(0.3), Color.blue.opacity(0.2)],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 20))
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(
                        LinearGradient(
                            colors: [.purple.opacity(0.5), .blue.opacity(0.3)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1
                    )
            )
        }
    }

    // MARK: - More Services

    private var moreServicesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("More Services")
                .font(.headline)
                .fontWeight(.bold)
                .foregroundColor(.primary)

            LazyVGrid(columns: [
                GridItem(.flexible(), spacing: 8),
                GridItem(.flexible(), spacing: 8),
                GridItem(.flexible(), spacing: 8)
            ], spacing: 10) {
                ForEach(Array(moreServices.enumerated()), id: \.element.id) { index, service in
                    MoreServiceItem(service: service, index: index)
                        .opacity(animateMoreServices ? 1 : 0)
                        .offset(y: animateMoreServices ? 0 : 15)
                        .animation(
                            .spring(response: 0.45, dampingFraction: 0.7)
                            .delay(Double(index) * 0.08),
                            value: animateMoreServices
                        )
                        .onTapGesture {
                            handleServiceTap(service)
                        }
                }
            }
            .padding(.horizontal, -4)
        }
    }

    // MARK: - Recent Activity

    private var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recent Activity")
                .font(.headline)
                .fontWeight(.bold)
                .foregroundColor(.primary)

            VStack(spacing: 12) {
                RecentActivityRow(
                    icon: "sparkles",
                    iconColor: .orange,
                    title: "Aries Horoscope",
                    subtitle: "Today's reading",
                    time: "2h ago"
                )

                RecentActivityRow(
                    icon: "cloud.sun.fill",
                    iconColor: .cyan,
                    title: "Weather in Delhi",
                    subtitle: "32°C, Partly Cloudy",
                    time: "5h ago"
                )

                RecentActivityRow(
                    icon: "tram.fill",
                    iconColor: .blue,
                    title: "PNR Status",
                    subtitle: "Confirmed - 2345678901",
                    time: "Yesterday"
                )
            }
            .padding(16)
            .background(Color(.systemGray6))
            .clipShape(RoundedRectangle(cornerRadius: 20))
        }
    }

    // MARK: - Helpers

    private func updateGreeting() {
        let hour = Calendar.current.component(.hour, from: Date())
        switch hour {
        case 5..<12: greeting = "Good Morning"
        case 12..<17: greeting = "Good Afternoon"
        case 17..<21: greeting = "Good Evening"
        default: greeting = "Good Night"
        }
    }

    private func handleServiceTap(_ service: AppService) {
        chatPrefill = servicePrompt(for: service)
        showChat = true
    }

    private func servicePrompt(for service: AppService) -> String {
        switch service.id.lowercased() {
        case "astrology":
            return "I'm an Aries. What's my horoscope for today?"
        case "news":
            return "What are today's top news headlines in India?"
        case "weather":
            return "What's the weather like in my city today?"
        case "travel":
            return "Check PNR status for my train booking"
        case "jobs":
            return "Show me the latest government job openings"
        case "cricket":
            return "Get the live cricket score right now"
        case "images":
            return "Generate an image of a futuristic city skyline"
        case "stocks":
            return "Give me today's market overview"
        case "food":
            return "Find good food places near me"
        case "reminder":
            return "Set a reminder to drink water every 2 hours"
        case "translate":
            return "Translate 'Hello, how are you?' to Hindi"
        case "calculator":
            return "Calculate 18% GST on 1250"
        case "facts":
            return "Fact-check this claim for me"
        case "games":
            return "Let's play a word game"
        default:
            return "Help me with \(service.name.lowercased())"
        }
    }

    /// Triggers staggered entry animations for all sections
    private func triggerEntryAnimations() {
        // Header slides down
        withAnimation(.spring(response: 0.6, dampingFraction: 0.8).delay(0.1)) {
            animateHeader = true
        }

        // Search bar scales in
        withAnimation(.spring(response: 0.5, dampingFraction: 0.75).delay(0.2)) {
            animateSearch = true
        }

        // Quick actions slide up
        withAnimation(.spring(response: 0.5, dampingFraction: 0.7).delay(0.3)) {
            animateQuickActions = true
        }

        // Premium banner slides from left
        withAnimation(.spring(response: 0.6, dampingFraction: 0.75).delay(0.4)) {
            animatePremiumBanner = true
        }

        // Services grid fades in (individual items animate separately)
        withAnimation(.spring(response: 0.5, dampingFraction: 0.8).delay(0.5)) {
            animateServices = true
        }

        // AI banner scales in
        withAnimation(.spring(response: 0.6, dampingFraction: 0.7).delay(0.7)) {
            animateAIBanner = true
        }

        // More services slides up
        withAnimation(.spring(response: 0.5, dampingFraction: 0.75).delay(0.85)) {
            animateMoreServices = true
        }

        // Recent activity slides up
        withAnimation(.spring(response: 0.5, dampingFraction: 0.75).delay(1.0)) {
            animateRecentActivity = true
        }
    }
}

// MARK: - Supporting Views

struct QuickAction {
    let icon: String
    let title: String
    let color: Color
    let action: String
}

struct QuickActionButton: View {
    let action: QuickAction
    let index: Int
    let onTap: () -> Void

    @State private var iconAnimated = false
    @State private var iconScale: CGFloat = 0.5

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 8) {
                Image(systemName: action.icon)
                    .font(.system(size: 22))
                    .foregroundColor(action.color)
                    .scaleEffect(iconScale)
                    .opacity(iconAnimated ? 1 : 0)

                Text(action.title)
                    .font(.caption2)
                    .fontWeight(.medium)
                    .foregroundColor(.primary.opacity(0.8))
                    .opacity(iconAnimated ? 1 : 0)
            }
            .frame(maxWidth: .infinity)
        }
        .onAppear {
            let delay = Double(index) * 0.1 + 0.2
            withAnimation(.spring(response: 0.5, dampingFraction: 0.6).delay(delay)) {
                iconAnimated = true
                iconScale = 1.0
            }
        }
    }
}

struct AppService: Identifiable {
    let id: String
    let name: String
    let icon: String
    let color: Color
    let gradient: [Color]
    let subtitle: String
}

struct ServiceGridItem: View {
    let service: AppService
    let index: Int

    @State private var isPressed = false
    @State private var iconAnimated = false
    @State private var iconRotation: Double = 0
    @State private var iconBounce: CGFloat = 0

    var body: some View {
        VStack(spacing: 10) {
            ZStack {
                // Glow ring behind icon
                Circle()
                    .fill(service.color.opacity(0.3))
                    .frame(width: 58, height: 58)
                    .scaleEffect(iconAnimated ? 1.0 : 0.5)
                    .opacity(iconAnimated ? 0.5 : 0)
                    .blur(radius: 4)

                Circle()
                    .fill(
                        LinearGradient(
                            colors: service.gradient,
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 52, height: 52)
                    .shadow(color: service.color.opacity(0.4), radius: 8, y: 4)
                    .scaleEffect(iconAnimated ? 1.0 : 0.7)

                Image(systemName: service.icon)
                    .font(.system(size: 22))
                    .foregroundColor(.white)
                    .rotationEffect(.degrees(iconRotation))
                    .offset(y: iconBounce)
            }

            Text(service.name)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.primary)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .scaleEffect(isPressed ? 0.92 : 1)
        .animation(.spring(response: 0.3), value: isPressed)
        .onLongPressGesture(minimumDuration: .infinity, pressing: { pressing in
            isPressed = pressing
        }, perform: {})
        .onAppear {
            // Staggered icon animation based on index
            let delay = Double(index) * 0.08 + 0.3

            withAnimation(.spring(response: 0.5, dampingFraction: 0.6).delay(delay)) {
                iconAnimated = true
            }

            // Small bounce effect on icon
            withAnimation(.spring(response: 0.4, dampingFraction: 0.5).delay(delay + 0.1)) {
                iconBounce = -4
            }

            // Return from bounce
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7).delay(delay + 0.25)) {
                iconBounce = 0
            }

            // Subtle rotation wiggle
            withAnimation(.easeOut(duration: 0.3).delay(delay + 0.15)) {
                iconRotation = 8
            }
            withAnimation(.spring(response: 0.4, dampingFraction: 0.5).delay(delay + 0.3)) {
                iconRotation = 0
            }
        }
    }
}

struct MoreServiceItem: View {
    let service: AppService
    let index: Int

    @State private var iconAnimated = false

    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                RoundedRectangle(cornerRadius: 14)
                    .fill(service.color.opacity(0.15))
                    .frame(width: 48, height: 48)
                    .scaleEffect(iconAnimated ? 1.0 : 0.8)

                Image(systemName: service.icon)
                    .font(.system(size: 20))
                    .foregroundColor(service.color)
                    .scaleEffect(iconAnimated ? 1.0 : 0.5)
                    .rotationEffect(.degrees(iconAnimated ? 0 : -15))
            }

            Text(service.name)
                .font(.caption2)
                .fontWeight(.medium)
                .foregroundColor(.primary.opacity(0.8))
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .onAppear {
            let delay = Double(index) * 0.1
            withAnimation(.spring(response: 0.5, dampingFraction: 0.6).delay(delay)) {
                iconAnimated = true
            }
        }
    }
}

struct RecentActivityRow: View {
    let icon: String
    let iconColor: Color
    let title: String
    let subtitle: String
    let time: String

    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                Circle()
                    .fill(iconColor.opacity(0.2))
                    .frame(width: 44, height: 44)

                Image(systemName: icon)
                    .font(.system(size: 18))
                    .foregroundColor(iconColor)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)

                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Text(time)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

struct ServiceDetailSheet: View {
    let service: AppService
    let onOpenChat: () -> Void
    let onUpgrade: () -> Void
    @Environment(\.dismiss) private var dismiss
    @Environment(\.colorScheme) private var colorScheme
    @StateObject private var subscriptionManager = SubscriptionManager.shared

    // Animation states
    @State private var animateIcon = false
    @State private var animateTitle = false
    @State private var animateContent = false
    @State private var animateButton = false

    // Map service to premium feature
    private var relatedFeature: PremiumFeature? {
        switch service.id {
        case "astrology": return .detailedKundli
        case "travel": return .trainTracking
        case "images": return .aiImageGeneration
        case "jobs": return .jobAlerts
        case "news": return .personalizedNews
        default: return nil
        }
    }

    private var isPremiumService: Bool {
        guard let feature = relatedFeature else { return false }
        return subscriptionManager.requiresUpgrade(for: feature)
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color(.systemBackground).ignoresSafeArea()

                VStack(spacing: 24) {
                    // Service Icon
                    ZStack {
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: service.gradient,
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .frame(width: 80, height: 80)

                        Image(systemName: service.icon)
                            .font(.system(size: 36))
                            .foregroundColor(.white)

                        // Premium badge
                        if isPremiumService {
                            Circle()
                                .fill(Color(.systemBackground))
                                .frame(width: 28, height: 28)
                                .overlay(
                                    Image(systemName: "crown.fill")
                                        .font(.system(size: 14))
                                        .foregroundColor(.orange)
                                )
                                .offset(x: 28, y: -28)
                        }
                    }
                    .scaleEffect(animateIcon ? 1 : 0.5)
                    .opacity(animateIcon ? 1 : 0)

                    VStack(spacing: 8) {
                        HStack(spacing: 8) {
                            Text(service.name)
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.primary)

                            if isPremiumService {
                                Text("PRO")
                                    .font(.system(size: 10, weight: .bold))
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
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

                        Text(service.subtitle)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .opacity(animateTitle ? 1 : 0)
                    .offset(y: animateTitle ? 0 : 10)

                    // Premium upgrade prompt (if needed)
                    if isPremiumService, let feature = relatedFeature {
                        MiniPaywall(feature: feature) {
                            dismiss()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                                onUpgrade()
                            }
                        }
                        .padding(.horizontal, 24)
                    }

                    // Service-specific suggestions
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Quick Actions")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.secondary)
                            .padding(.horizontal, 24)

                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 10) {
                                ForEach(suggestionsForService(service), id: \.self) { suggestion in
                                    ServiceSuggestionChip(text: suggestion) {
                                        dismiss()
                                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                                            onOpenChat()
                                        }
                                    }
                                }
                            }
                            .padding(.horizontal, 24)
                        }
                    }
                    .opacity(animateContent ? 1 : 0)
                    .offset(y: animateContent ? 0 : 15)

                    // Open in Chat button
                    Button(action: {
                        dismiss()
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            onOpenChat()
                        }
                    }) {
                        HStack {
                            Image(systemName: "bubble.left.and.bubble.right.fill")
                            Text("Ask D23 AI about \(service.name)")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            LinearGradient(
                                colors: service.gradient,
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                    }
                    .padding(.horizontal, 24)
                    .opacity(animateButton ? 1 : 0)
                    .offset(y: animateButton ? 0 : 20)

                    Spacer()
                }
                .padding(.top, 40)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
        .onAppear {
            withAnimation(.spring(response: 0.5, dampingFraction: 0.7).delay(0.1)) {
                animateIcon = true
            }
            withAnimation(.spring(response: 0.45, dampingFraction: 0.75).delay(0.2)) {
                animateTitle = true
            }
            withAnimation(.spring(response: 0.5, dampingFraction: 0.7).delay(0.35)) {
                animateContent = true
            }
            withAnimation(.spring(response: 0.55, dampingFraction: 0.7).delay(0.5)) {
                animateButton = true
            }
        }
    }

    private func suggestionsForService(_ service: AppService) -> [String] {
        switch service.id {
        case "astrology":
            return ["Today's Horoscope", "Kundli", "Lucky Numbers", "Compatibility"]
        case "news":
            return ["Top Headlines", "Tech News", "Sports News", "Business"]
        case "weather":
            return ["Current Weather", "7-Day Forecast", "Rain Alert"]
        case "travel":
            return ["Check PNR", "Train Status", "Live Running"]
        case "jobs":
            return ["Latest Jobs", "SSC Jobs", "Railway Jobs", "Bank Jobs"]
        case "cricket":
            return ["Live Score", "Upcoming Matches", "IPL Schedule"]
        case "images":
            return ["Generate Image", "Edit Photo", "AI Art"]
        case "stocks":
            return ["Market Summary", "Sensex", "Nifty 50"]
        default:
            return ["Get Started"]
        }
    }
}

struct ServiceSuggestionChip: View {
    let text: String
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            Text(text)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.primary)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(Color(.systemGray5))
                .clipShape(Capsule())
                .overlay(
                    Capsule()
                        .stroke(Color(.systemGray4), lineWidth: 1)
                )
        }
    }
}

// MARK: - Background

struct SuperAppBackground: View {
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        ZStack {
            // Adaptive base color
            (colorScheme == .dark ? Color.black : Color(red: 0.98, green: 0.98, blue: 0.99))
                .ignoresSafeArea()

            // Gradient overlay
            LinearGradient(
                colors: colorScheme == .dark ? [
                    Color.purple.opacity(0.15),
                    Color.blue.opacity(0.1),
                    Color.black
                ] : [
                    Color.purple.opacity(0.08),
                    Color.blue.opacity(0.05),
                    Color(red: 0.98, green: 0.98, blue: 0.99)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            // Subtle pattern
            GeometryReader { geometry in
                ForEach(0..<3, id: \.self) { i in
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [Color.purple.opacity(colorScheme == .dark ? 0.1 : 0.06), .clear],
                                center: .center,
                                startRadius: 0,
                                endRadius: 150
                            )
                        )
                        .frame(width: 300, height: 300)
                        .offset(
                            x: CGFloat(i) * 150 - 100,
                            y: CGFloat(i) * 200 - 100
                        )
                        .blur(radius: 50)
                }
            }
        }
    }
}

// MARK: - Preview

#Preview {
    SuperAppHomeView()
        .environmentObject(AuthManager.shared)
}
