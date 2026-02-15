import SwiftUI

/// Interactive Super App Onboarding - "One App, Many Solutions"
struct SuperAppOnboardingView: View {
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    @State private var currentPage = 0
    @State private var animateHero = false
    @State private var showServices = false
    @State private var selectedServices: Set<String> = []
    @State private var userName = ""
    @State private var dragOffset: CGFloat = 0

    private let pages = SuperAppPage.allPages

    var body: some View {
        ZStack {
            // Animated Background
            AnimatedSuperAppBackground(page: currentPage)

            VStack(spacing: 0) {
                // Skip Button
                HStack {
                    Spacer()
                    if currentPage < pages.count - 1 {
                        Button("Skip") {
                            withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
                                currentPage = pages.count - 1
                            }
                        }
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.white.opacity(0.7))
                        .padding()
                    }
                }

                // Page Content
                TabView(selection: $currentPage) {
                    // Page 1: Welcome - One App Many Solutions
                    WelcomePage(animate: $animateHero)
                        .tag(0)

                    // Page 2: Services Showcase
                    ServicesShowcasePage(showServices: $showServices)
                        .tag(1)

                    // Page 3: Pick Your Services
                    ServicePickerPage(selectedServices: $selectedServices)
                        .tag(2)

                    // Page 4: Personalize
                    PersonalizePage(userName: $userName)
                        .tag(3)

                    // Page 5: Ready to Go
                    ReadyPage(selectedServices: selectedServices, userName: userName) {
                        withAnimation {
                            hasCompletedOnboarding = true
                        }
                    }
                    .tag(4)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                .onChange(of: currentPage) { _, newValue in
                    triggerPageAnimations(for: newValue)
                }

                // Custom Page Indicator & Navigation
                VStack(spacing: 20) {
                    // Page Dots
                    HStack(spacing: 8) {
                        ForEach(0..<pages.count, id: \.self) { index in
                            Capsule()
                                .fill(index == currentPage ? Color.white : Color.white.opacity(0.3))
                                .frame(width: index == currentPage ? 24 : 8, height: 8)
                                .animation(.spring(response: 0.3), value: currentPage)
                        }
                    }

                    // Navigation Buttons
                    HStack(spacing: 16) {
                        if currentPage > 0 {
                            Button(action: {
                                withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                                    currentPage -= 1
                                }
                            }) {
                                HStack(spacing: 6) {
                                    Image(systemName: "chevron.left")
                                    Text("Back")
                                }
                                .font(.subheadline)
                                .fontWeight(.semibold)
                                .foregroundColor(.white.opacity(0.8))
                                .padding(.horizontal, 20)
                                .padding(.vertical, 12)
                                .background(Color.white.opacity(0.15))
                                .clipShape(Capsule())
                            }
                        }

                        Spacer()

                        if currentPage < pages.count - 1 {
                            Button(action: {
                                withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                                    currentPage += 1
                                }
                            }) {
                                HStack(spacing: 6) {
                                    Text(currentPage == 2 ? "Continue" : "Next")
                                    Image(systemName: "chevron.right")
                                }
                                .font(.subheadline)
                                .fontWeight(.semibold)
                                .foregroundColor(.black)
                                .padding(.horizontal, 24)
                                .padding(.vertical, 12)
                                .background(
                                    LinearGradient(
                                        colors: [.white, .white.opacity(0.9)],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .clipShape(Capsule())
                                .shadow(color: .white.opacity(0.3), radius: 10, y: 5)
                            }
                        }
                    }
                    .padding(.horizontal, 24)
                }
                .padding(.bottom, 40)
            }
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                withAnimation(.spring(response: 0.8, dampingFraction: 0.7)) {
                    animateHero = true
                }
            }
        }
    }

    private func triggerPageAnimations(for page: Int) {
        switch page {
        case 1:
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                withAnimation(.spring(response: 0.6, dampingFraction: 0.7)) {
                    showServices = true
                }
            }
        default:
            break
        }
    }
}

// MARK: - Onboarding Pages

struct SuperAppPage {
    let title: String
    let subtitle: String
    let icon: String

    static let allPages = [
        SuperAppPage(title: "Welcome", subtitle: "One App, Many Solutions", icon: "sparkles"),
        SuperAppPage(title: "Services", subtitle: "Everything You Need", icon: "square.grid.2x2"),
        SuperAppPage(title: "Customize", subtitle: "Pick Your Favorites", icon: "heart.fill"),
        SuperAppPage(title: "Personalize", subtitle: "Make It Yours", icon: "person.fill"),
        SuperAppPage(title: "Ready", subtitle: "Let's Get Started", icon: "rocket.fill"),
    ]
}

// MARK: - Page 1: Welcome

struct WelcomePage: View {
    @Binding var animate: Bool

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            // Animated Logo/Hero
            ZStack {
                // Outer rings
                ForEach(0..<3, id: \.self) { i in
                    Circle()
                        .stroke(
                            LinearGradient(
                                colors: [.purple.opacity(0.3), .blue.opacity(0.2), .clear],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 2
                        )
                        .frame(width: CGFloat(120 + i * 50), height: CGFloat(120 + i * 50))
                        .rotationEffect(.degrees(animate ? Double(i * 120) : 0))
                        .animation(
                            .linear(duration: Double(8 + i * 2))
                            .repeatForever(autoreverses: false),
                            value: animate
                        )
                }

                // Service icons orbiting
                ForEach(ServiceItem.featured.indices, id: \.self) { index in
                    let service = ServiceItem.featured[index]
                    let angle = Double(index) * (360.0 / Double(ServiceItem.featured.count))

                    Image(systemName: service.icon)
                        .font(.system(size: 20))
                        .foregroundColor(service.color)
                        .frame(width: 44, height: 44)
                        .background(service.color.opacity(0.2))
                        .clipShape(Circle())
                        .offset(x: animate ? cos(angle * .pi / 180) * 100 : 0,
                                y: animate ? sin(angle * .pi / 180) * 100 : 0)
                        .opacity(animate ? 1 : 0)
                        .animation(
                            .spring(response: 0.8, dampingFraction: 0.6)
                            .delay(Double(index) * 0.1),
                            value: animate
                        )
                }

                // Center logo
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.purple, .blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 80, height: 80)
                        .shadow(color: .purple.opacity(0.5), radius: 20, y: 10)

                    Text("D23")
                        .font(.system(size: 28, weight: .heavy, design: .rounded))
                        .foregroundColor(.white)
                }
                .scaleEffect(animate ? 1 : 0.5)
                .opacity(animate ? 1 : 0)
            }
            .frame(height: 280)

            // Title
            VStack(spacing: 12) {
                Text("One App")
                    .font(.system(size: 42, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)

                HStack(spacing: 8) {
                    Text("Many")
                        .font(.system(size: 42, weight: .heavy, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Text("Solutions")
                        .font(.system(size: 42, weight: .heavy, design: .rounded))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.purple, .blue, .cyan],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                }
            }
            .opacity(animate ? 1 : 0)
            .offset(y: animate ? 0 : 20)

            Text("AI Assistant • Astrology • Travel • News\nWeather • Jobs • And Much More")
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.6))
                .opacity(animate ? 1 : 0)
                .offset(y: animate ? 0 : 10)

            Spacer()
            Spacer()
        }
        .padding(.horizontal, 24)
    }
}

// MARK: - Page 2: Services Showcase

struct ServicesShowcasePage: View {
    @Binding var showServices: Bool
    @State private var hoveredService: String?

    let services = ServiceItem.all

    let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16)
    ]

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            // Title
            VStack(spacing: 8) {
                Text("Everything You Need")
                    .font(.system(size: 28, weight: .bold, design: .rounded))
                    .foregroundColor(.white)

                Text("All your daily tasks in one place")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.6))
            }

            // Services Grid
            LazyVGrid(columns: columns, spacing: 16) {
                ForEach(services.indices, id: \.self) { index in
                    let service = services[index]
                    ServiceShowcaseCard(service: service)
                        .opacity(showServices ? 1 : 0)
                        .offset(y: showServices ? 0 : 30)
                        .animation(
                            .spring(response: 0.5, dampingFraction: 0.7)
                            .delay(Double(index) * 0.05),
                            value: showServices
                        )
                }
            }
            .padding(.horizontal, 20)

            Spacer()
        }
    }
}

struct ServiceShowcaseCard: View {
    let service: ServiceItem
    @State private var isPressed = false

    var body: some View {
        VStack(spacing: 10) {
            ZStack {
                Circle()
                    .fill(service.color.opacity(0.2))
                    .frame(width: 56, height: 56)

                Image(systemName: service.icon)
                    .font(.system(size: 24))
                    .foregroundColor(service.color)
            }

            Text(service.name)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.white)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 16)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .scaleEffect(isPressed ? 0.95 : 1)
        .onTapGesture {
            withAnimation(.spring(response: 0.3)) {
                isPressed = true
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                withAnimation(.spring(response: 0.3)) {
                    isPressed = false
                }
            }
        }
    }
}

// MARK: - Page 3: Service Picker

struct ServicePickerPage: View {
    @Binding var selectedServices: Set<String>

    let services = ServiceItem.all

    let columns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12)
    ]

    var body: some View {
        VStack(spacing: 20) {
            Spacer().frame(height: 20)

            // Title
            VStack(spacing: 8) {
                Text("What interests you?")
                    .font(.system(size: 26, weight: .bold, design: .rounded))
                    .foregroundColor(.white)

                Text("Select your favorite services")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.6))

                // Selection count
                Text("\(selectedServices.count) selected")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.purple)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.purple.opacity(0.2))
                    .clipShape(Capsule())
            }

            // Services Grid
            ScrollView(showsIndicators: false) {
                LazyVGrid(columns: columns, spacing: 12) {
                    ForEach(services, id: \.id) { service in
                        ServicePickerCard(
                            service: service,
                            isSelected: selectedServices.contains(service.id)
                        ) {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                                if selectedServices.contains(service.id) {
                                    selectedServices.remove(service.id)
                                } else {
                                    selectedServices.insert(service.id)
                                }
                            }
                        }
                    }
                }
                .padding(.horizontal, 20)
            }

            Spacer()
        }
    }
}

struct ServicePickerCard: View {
    let service: ServiceItem
    let isSelected: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 12) {
                HStack {
                    Spacer()
                    Image(systemName: isSelected ? "checkmark.circle.fill" : "circle")
                        .font(.system(size: 20))
                        .foregroundColor(isSelected ? service.color : .white.opacity(0.3))
                }

                ZStack {
                    Circle()
                        .fill(isSelected ? service.color : service.color.opacity(0.2))
                        .frame(width: 52, height: 52)

                    Image(systemName: service.icon)
                        .font(.system(size: 24))
                        .foregroundColor(isSelected ? .white : service.color)
                }

                VStack(spacing: 4) {
                    Text(service.name)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)

                    Text(service.shortDescription)
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.5))
                        .lineLimit(1)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 14)
            .frame(maxWidth: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.white.opacity(isSelected ? 0.12 : 0.06))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(isSelected ? service.color.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Page 4: Personalize

struct PersonalizePage: View {
    @Binding var userName: String
    @FocusState private var isNameFocused: Bool

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            // Avatar
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple.opacity(0.3), .blue.opacity(0.3)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 120, height: 120)

                if userName.isEmpty {
                    Image(systemName: "person.fill")
                        .font(.system(size: 50))
                        .foregroundColor(.white.opacity(0.5))
                } else {
                    Text(String(userName.prefix(1)).uppercased())
                        .font(.system(size: 50, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                }
            }

            // Title
            VStack(spacing: 8) {
                Text("What should we call you?")
                    .font(.system(size: 26, weight: .bold, design: .rounded))
                    .foregroundColor(.white)

                Text("Personalize your experience")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.6))
            }

            // Name Input
            VStack(spacing: 8) {
                TextField("", text: $userName, prompt: Text("Enter your name").foregroundColor(.white.opacity(0.4)))
                    .font(.title3)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                    .padding()
                    .background(Color.white.opacity(0.1))
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .focused($isNameFocused)
                    .onSubmit {
                        isNameFocused = false
                    }

                Text("You can change this later in settings")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.4))
            }
            .padding(.horizontal, 40)

            Spacer()
            Spacer()
        }
    }
}

// MARK: - Page 5: Ready

struct ReadyPage: View {
    let selectedServices: Set<String>
    let userName: String
    let onGetStarted: () -> Void

    @State private var animate = false
    @State private var showConfetti = false

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            // Celebration Animation
            ZStack {
                // Success checkmark
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.green, .mint],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 100, height: 100)
                    .scaleEffect(animate ? 1 : 0)
                    .shadow(color: .green.opacity(0.5), radius: 20, y: 10)

                Image(systemName: "checkmark")
                    .font(.system(size: 50, weight: .bold))
                    .foregroundColor(.white)
                    .scaleEffect(animate ? 1 : 0)
                    .rotationEffect(.degrees(animate ? 0 : -90))
            }

            // Greeting
            VStack(spacing: 12) {
                if !userName.isEmpty {
                    Text("Welcome, \(userName)!")
                        .font(.system(size: 28, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                } else {
                    Text("You're All Set!")
                        .font(.system(size: 28, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                }

                Text("Your personalized D23 experience is ready")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.6))
            }

            // Selected Services Summary
            if !selectedServices.isEmpty {
                VStack(spacing: 12) {
                    Text("Your selected services")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.5))

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(ServiceItem.all.filter { selectedServices.contains($0.id) }) { service in
                                HStack(spacing: 6) {
                                    Image(systemName: service.icon)
                                        .font(.caption)
                                    Text(service.name)
                                        .font(.caption)
                                        .fontWeight(.medium)
                                }
                                .foregroundColor(service.color)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(service.color.opacity(0.2))
                                .clipShape(Capsule())
                            }
                        }
                        .padding(.horizontal, 20)
                    }
                }
            }

            Spacer()

            // Get Started Button
            Button(action: onGetStarted) {
                HStack(spacing: 10) {
                    Text("Get Started")
                        .font(.headline)
                        .fontWeight(.bold)
                    Image(systemName: "arrow.right")
                        .font(.headline)
                }
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 18)
                .background(
                    LinearGradient(
                        colors: [.white, .white.opacity(0.95)],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .clipShape(RoundedRectangle(cornerRadius: 16))
                .shadow(color: .white.opacity(0.3), radius: 15, y: 8)
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 60)
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                withAnimation(.spring(response: 0.6, dampingFraction: 0.6)) {
                    animate = true
                }
            }
        }
    }
}

// MARK: - Service Model

struct ServiceItem: Identifiable {
    let id: String
    let name: String
    let icon: String
    let color: Color
    let shortDescription: String

    static let featured: [ServiceItem] = [
        ServiceItem(id: "chat", name: "AI Chat", icon: "bubble.left.and.bubble.right.fill", color: .purple, shortDescription: "Smart assistant"),
        ServiceItem(id: "astro", name: "Astrology", icon: "sparkles", color: .orange, shortDescription: "Daily horoscope"),
        ServiceItem(id: "news", name: "News", icon: "newspaper.fill", color: .red, shortDescription: "Latest updates"),
        ServiceItem(id: "weather", name: "Weather", icon: "cloud.sun.fill", color: .cyan, shortDescription: "Forecasts"),
        ServiceItem(id: "travel", name: "Travel", icon: "tram.fill", color: .blue, shortDescription: "PNR & trains"),
        ServiceItem(id: "jobs", name: "Jobs", icon: "briefcase.fill", color: .green, shortDescription: "Sarkari Naukri"),
    ]

    static let all: [ServiceItem] = [
        ServiceItem(id: "chat", name: "AI Chat", icon: "bubble.left.and.bubble.right.fill", color: .purple, shortDescription: "Smart AI assistant"),
        ServiceItem(id: "astro", name: "Astrology", icon: "sparkles", color: .orange, shortDescription: "Horoscope & Kundli"),
        ServiceItem(id: "news", name: "News", icon: "newspaper.fill", color: .red, shortDescription: "Latest headlines"),
        ServiceItem(id: "weather", name: "Weather", icon: "cloud.sun.fill", color: .cyan, shortDescription: "Live forecasts"),
        ServiceItem(id: "travel", name: "Travel", icon: "tram.fill", color: .blue, shortDescription: "PNR & train status"),
        ServiceItem(id: "jobs", name: "Govt Jobs", icon: "briefcase.fill", color: .green, shortDescription: "Sarkari Naukri"),
        ServiceItem(id: "cricket", name: "Cricket", icon: "sportscourt.fill", color: .mint, shortDescription: "Live scores"),
        ServiceItem(id: "images", name: "AI Images", icon: "photo.fill", color: .pink, shortDescription: "Generate images"),
        ServiceItem(id: "reminder", name: "Reminders", icon: "bell.fill", color: .yellow, shortDescription: "Never forget"),
        ServiceItem(id: "food", name: "Food", icon: "fork.knife", color: .orange, shortDescription: "Nearby places"),
        ServiceItem(id: "stocks", name: "Stocks", icon: "chart.line.uptrend.xyaxis", color: .green, shortDescription: "Market updates"),
        ServiceItem(id: "translate", name: "Translate", icon: "character.bubble.fill", color: .indigo, shortDescription: "22+ languages"),
    ]
}

// MARK: - Animated Background

struct AnimatedSuperAppBackground: View {
    let page: Int

    @State private var animate = false

    private var gradientColors: [Color] {
        switch page {
        case 0: return [Color(red: 0.1, green: 0.05, blue: 0.2), Color(red: 0.05, green: 0.02, blue: 0.1)]
        case 1: return [Color(red: 0.05, green: 0.1, blue: 0.2), Color(red: 0.02, green: 0.05, blue: 0.1)]
        case 2: return [Color(red: 0.15, green: 0.05, blue: 0.1), Color(red: 0.08, green: 0.02, blue: 0.05)]
        case 3: return [Color(red: 0.05, green: 0.1, blue: 0.15), Color(red: 0.02, green: 0.05, blue: 0.08)]
        case 4: return [Color(red: 0.05, green: 0.12, blue: 0.1), Color(red: 0.02, green: 0.06, blue: 0.05)]
        default: return [Color.black, Color(red: 0.05, green: 0.02, blue: 0.1)]
        }
    }

    var body: some View {
        ZStack {
            // Base gradient
            LinearGradient(
                colors: gradientColors,
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            .animation(.easeInOut(duration: 0.5), value: page)

            // Floating orbs
            ForEach(0..<5, id: \.self) { i in
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [orbColor(for: i).opacity(0.3), .clear],
                            center: .center,
                            startRadius: 0,
                            endRadius: 100
                        )
                    )
                    .frame(width: CGFloat.random(in: 100...200))
                    .offset(
                        x: animate ? CGFloat.random(in: -100...100) : CGFloat.random(in: -50...50),
                        y: animate ? CGFloat.random(in: -200...200) : CGFloat.random(in: -100...100)
                    )
                    .blur(radius: 30)
            }
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 8).repeatForever(autoreverses: true)) {
                animate = true
            }
        }
    }

    private func orbColor(for index: Int) -> Color {
        let colors: [Color] = [.purple, .blue, .cyan, .pink, .orange]
        return colors[index % colors.count]
    }
}

// MARK: - Preview

#Preview {
    SuperAppOnboardingView()
}
