import SwiftUI

/// Main Tab View for Super App Layout
struct SuperAppTabView: View {
    @State private var selectedTab = 0
    @State private var showChat = false
    @StateObject private var conversationListVM = DependencyContainer.shared.makeConversationListViewModel()
    @StateObject private var gmailVM = DependencyContainer.shared.makeGmailViewModel()
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject private var themeManager: ThemeManager

    var body: some View {
        ZStack(alignment: .bottom) {
            // Tab Content
            TabView(selection: $selectedTab) {
                SuperAppHomeView()
                    .tag(0)

                NavigationStack {
                    ChatView(conversationId: nil)
                }
                    .tag(1)

                ConversationListView(viewModel: conversationListVM)
                    .tag(2)

                GmailInboxView(viewModel: gmailVM)
                    .tag(3)

                SettingsView()
                    .tag(4)
            }
            .tabViewStyle(.page(indexDisplayMode: .never))

            // Custom Tab Bar
            CustomTabBar(selectedTab: $selectedTab, showChat: $showChat)
        }
        .ignoresSafeArea(.keyboard)
        .fullScreenCover(isPresented: $showChat) {
            NavigationStack {
                ChatView(conversationId: nil)
            }
        }
    }
}

// MARK: - Custom Tab Bar

struct CustomTabBar: View {
    @Binding var selectedTab: Int
    @Binding var showChat: Bool
    @EnvironmentObject private var themeManager: ThemeManager

    let tabs: [(icon: String, label: String)] = [
        ("house.fill", "Home"),
        ("bubble.left.and.bubble.right.fill", "Chat"),
        ("clock.fill", "History"),
        ("envelope.fill", "Gmail"),
        ("gearshape.fill", "Settings")
    ]

    var body: some View {
        HStack(spacing: 0) {
            ForEach(tabs.indices, id: \.self) { index in
                if index == 1 {
                    // Center AI Button
                    CenterAIButton {
                        showChat = true
                    }
                } else {
                    TabBarButton(
                        icon: tabs[index].icon,
                        label: tabs[index].label,
                        isSelected: selectedTab == index
                    ) {
                        withAnimation(.spring(response: 0.3)) {
                            selectedTab = index
                        }
                    }
                }
            }
        }
        .padding(.horizontal, 8)
        .padding(.top, 8)
        .safeAreaPadding(.bottom, 10)
        .background(
            TabBarBackground()
        )
        .shadow(
            color: themeManager.isLightMode ? themeManager.lightShadowColor : .clear,
            radius: 8,
            y: -2
        )
    }
}

struct TabBarButton: View {
    let icon: String
    let label: String
    let isSelected: Bool
    let action: () -> Void
    @EnvironmentObject private var themeManager: ThemeManager

    private var selectedColor: Color {
        themeManager.isLightMode ? themeManager.primaryColor : .white
    }

    private var unselectedColor: Color {
        themeManager.isLightMode ? .black.opacity(0.5) : .white.opacity(0.4)
    }

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 22))
                    .foregroundColor(isSelected ? selectedColor : unselectedColor)

                Text(label)
                    .font(.system(size: 10))
                    .fontWeight(.medium)
                    .foregroundColor(isSelected ? selectedColor : unselectedColor)
            }
            .frame(maxWidth: .infinity)
        }
    }
}

struct CenterAIButton: View {
    let action: () -> Void
    @State private var isPressed = false
    @State private var animate = false

    var body: some View {
        Button(action: action) {
            ZStack {
                // Glow effect
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [.purple.opacity(0.4), .clear],
                            center: .center,
                            startRadius: 20,
                            endRadius: 50
                        )
                    )
                    .frame(width: 80, height: 80)
                    .scaleEffect(animate ? 1.2 : 1)
                    .opacity(animate ? 0.5 : 0.8)

                // Button
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .blue],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 56, height: 56)
                    .shadow(color: .purple.opacity(0.5), radius: 12, y: 4)

                Image(systemName: "sparkles")
                    .font(.system(size: 24, weight: .semibold))
                    .foregroundColor(.white)
            }
            .offset(y: -20)
            .scaleEffect(isPressed ? 0.9 : 1)
        }
        .frame(maxWidth: .infinity)
        .onLongPressGesture(minimumDuration: .infinity, pressing: { pressing in
            withAnimation(.spring(response: 0.3)) {
                isPressed = pressing
            }
        }, perform: {})
        .onAppear {
            withAnimation(.spring(response: 0.5, dampingFraction: 0.7).delay(0.1)) {
                animate = true
            }
        }
    }
}

struct TabBarBackground: View {
    @EnvironmentObject private var themeManager: ThemeManager

    var body: some View {
        ZStack {
            if themeManager.isLightMode {
                Rectangle()
                    .fill(themeManager.lightElevatedSurface)

                LinearGradient(
                    colors: [
                        Color.white.opacity(0.95),
                        Color.black.opacity(0.03)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )

                VStack {
                    Rectangle()
                        .fill(themeManager.lightDividerColor)
                        .frame(height: 1)
                    Spacer()
                }
            } else {
                // Glass effect
                Rectangle()
                    .fill(.ultraThinMaterial)
                    .environment(\.colorScheme, .dark)

                // Gradient overlay
                LinearGradient(
                    colors: [
                        Color.black.opacity(0.8),
                        Color.black.opacity(0.95)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )

                // Top border
                VStack {
                    Rectangle()
                        .fill(
                            LinearGradient(
                                colors: [.purple.opacity(0.3), .blue.opacity(0.2), .clear],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(height: 1)
                    Spacer()
                }
            }
        }
    }
}

// MARK: - Preview

#Preview {
    SuperAppTabView()
        .environmentObject(AuthManager.shared)
}
