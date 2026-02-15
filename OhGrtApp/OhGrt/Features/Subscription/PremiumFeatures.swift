import Foundation
import SwiftUI

// MARK: - Premium Tier System

/// Premium subscription tiers with feature access
enum PremiumTier: String, CaseIterable {
    case free = "free"
    case plus = "plus"      // Monthly subscription
    case pro = "pro"        // Yearly subscription (best value)

    var displayName: String {
        switch self {
        case .free: return "Free"
        case .plus: return "Plus"
        case .pro: return "Pro"
        }
    }

    var badge: String {
        switch self {
        case .free: return ""
        case .plus: return "PLUS"
        case .pro: return "PRO"
        }
    }

    var badgeColor: Color {
        switch self {
        case .free: return .gray
        case .plus: return .blue
        case .pro: return .orange
        }
    }

    var badgeGradient: [Color] {
        switch self {
        case .free: return [.gray, .gray.opacity(0.7)]
        case .plus: return [.blue, .purple]
        case .pro: return [.orange, .pink]
        }
    }

    var icon: String {
        switch self {
        case .free: return "person.fill"
        case .plus: return "star.fill"
        case .pro: return "crown.fill"
        }
    }
}

// MARK: - Premium Feature Definitions

/// All premium features with their tier requirements
enum PremiumFeature: String, CaseIterable {
    // Chat Features
    case unlimitedMessages = "unlimited_messages"
    case priorityResponse = "priority_response"
    case chatHistory = "chat_history"

    // Astrology Features
    case dailyHoroscope = "daily_horoscope"
    case detailedKundli = "detailed_kundli"
    case compatibility = "compatibility"
    case tarotReading = "tarot_reading"
    case panchang = "panchang"

    // Travel Features
    case pnrStatus = "pnr_status"
    case trainTracking = "train_tracking"
    case multiPnr = "multi_pnr"

    // News & Info Features
    case newsHeadlines = "news_headlines"
    case personalizedNews = "personalized_news"
    case weatherForecast = "weather_forecast"
    case cricketLiveScore = "cricket_live_score"

    // Jobs Features
    case govtJobs = "govt_jobs"
    case jobAlerts = "job_alerts"
    case resumeBuilder = "resume_builder"

    // AI Features
    case aiImageGeneration = "ai_image_generation"
    case voiceChat = "voice_chat"
    case documentScan = "document_scan"

    // Premium Only Features
    case adFree = "ad_free"
    case exportData = "export_data"
    case customThemes = "custom_themes"
    case offlineMode = "offline_mode"

    /// Minimum tier required for this feature
    var minimumTier: PremiumTier {
        switch self {
        // Free tier features
        case .dailyHoroscope, .newsHeadlines, .weatherForecast,
             .pnrStatus, .govtJobs, .cricketLiveScore:
            return .free

        // Plus tier features
        case .unlimitedMessages, .chatHistory, .detailedKundli,
             .compatibility, .tarotReading, .panchang,
             .trainTracking, .personalizedNews, .jobAlerts,
             .voiceChat, .adFree:
            return .plus

        // Pro tier features
        case .priorityResponse, .multiPnr, .aiImageGeneration,
             .documentScan, .resumeBuilder, .exportData,
             .customThemes, .offlineMode:
            return .pro
        }
    }

    var displayName: String {
        switch self {
        case .unlimitedMessages: return "Unlimited Messages"
        case .priorityResponse: return "Priority Response"
        case .chatHistory: return "Chat History"
        case .dailyHoroscope: return "Daily Horoscope"
        case .detailedKundli: return "Detailed Kundli"
        case .compatibility: return "Compatibility Check"
        case .tarotReading: return "Tarot Reading"
        case .panchang: return "Panchang"
        case .pnrStatus: return "PNR Status"
        case .trainTracking: return "Live Train Tracking"
        case .multiPnr: return "Multi-PNR Tracking"
        case .newsHeadlines: return "News Headlines"
        case .personalizedNews: return "Personalized News"
        case .weatherForecast: return "Weather Forecast"
        case .cricketLiveScore: return "Cricket Live Score"
        case .govtJobs: return "Govt Jobs"
        case .jobAlerts: return "Job Alerts"
        case .resumeBuilder: return "Resume Builder"
        case .aiImageGeneration: return "AI Image Generation"
        case .voiceChat: return "Voice Chat"
        case .documentScan: return "Document Scanner"
        case .adFree: return "Ad-Free Experience"
        case .exportData: return "Export Data"
        case .customThemes: return "Custom Themes"
        case .offlineMode: return "Offline Mode"
        }
    }

    var icon: String {
        switch self {
        case .unlimitedMessages: return "infinity"
        case .priorityResponse: return "bolt.fill"
        case .chatHistory: return "clock.arrow.circlepath"
        case .dailyHoroscope: return "sparkles"
        case .detailedKundli: return "star.circle.fill"
        case .compatibility: return "heart.fill"
        case .tarotReading: return "suit.diamond.fill"
        case .panchang: return "calendar"
        case .pnrStatus: return "ticket.fill"
        case .trainTracking: return "train.side.front.car"
        case .multiPnr: return "list.bullet.clipboard.fill"
        case .newsHeadlines: return "newspaper.fill"
        case .personalizedNews: return "person.text.rectangle.fill"
        case .weatherForecast: return "cloud.sun.fill"
        case .cricketLiveScore: return "sportscourt.fill"
        case .govtJobs: return "briefcase.fill"
        case .jobAlerts: return "bell.badge.fill"
        case .resumeBuilder: return "doc.text.fill"
        case .aiImageGeneration: return "wand.and.stars"
        case .voiceChat: return "mic.fill"
        case .documentScan: return "doc.viewfinder"
        case .adFree: return "xmark.circle.fill"
        case .exportData: return "arrow.up.doc.fill"
        case .customThemes: return "paintbrush.fill"
        case .offlineMode: return "wifi.slash"
        }
    }

    var description: String {
        switch self {
        case .unlimitedMessages: return "Send unlimited messages to AI"
        case .priorityResponse: return "Get faster responses"
        case .chatHistory: return "Access complete chat history"
        case .dailyHoroscope: return "Daily zodiac predictions"
        case .detailedKundli: return "Complete birth chart analysis"
        case .compatibility: return "Love & compatibility match"
        case .tarotReading: return "Mystical tarot card readings"
        case .panchang: return "Hindu calendar & muhurat"
        case .pnrStatus: return "Check train booking status"
        case .trainTracking: return "Real-time train location"
        case .multiPnr: return "Track multiple PNRs at once"
        case .newsHeadlines: return "Latest news updates"
        case .personalizedNews: return "News based on your interests"
        case .weatherForecast: return "Accurate weather predictions"
        case .cricketLiveScore: return "Live cricket match scores"
        case .govtJobs: return "Latest government jobs"
        case .jobAlerts: return "Get notified for new jobs"
        case .resumeBuilder: return "Build professional resume"
        case .aiImageGeneration: return "Create AI-generated images"
        case .voiceChat: return "Talk to AI with voice"
        case .documentScan: return "Scan and extract text"
        case .adFree: return "No advertisements"
        case .exportData: return "Export your data"
        case .customThemes: return "Personalize app appearance"
        case .offlineMode: return "Use app without internet"
        }
    }
}

// MARK: - Usage Limits

/// Daily usage limits per tier for specific features
struct UsageLimits {
    let tier: PremiumTier

    var dailyMessages: Int {
        switch tier {
        case .free: return 10
        case .plus: return 100
        case .pro: return Int.max // Unlimited
        }
    }

    var dailyHoroscopes: Int {
        switch tier {
        case .free: return 3
        case .plus: return 20
        case .pro: return Int.max
        }
    }

    var dailyAiImages: Int {
        switch tier {
        case .free: return 0
        case .plus: return 5
        case .pro: return 50
        }
    }

    var dailyPnrChecks: Int {
        switch tier {
        case .free: return 5
        case .plus: return 20
        case .pro: return Int.max
        }
    }

    var savedPnrs: Int {
        switch tier {
        case .free: return 1
        case .plus: return 5
        case .pro: return Int.max
        }
    }

    var dailyNewsArticles: Int {
        switch tier {
        case .free: return 10
        case .plus: return 50
        case .pro: return Int.max
        }
    }

    var chatHistoryDays: Int {
        switch tier {
        case .free: return 1
        case .plus: return 30
        case .pro: return Int.max
        }
    }
}

// MARK: - Pricing Configuration

struct PricingConfig {
    static let monthlyProductId = "com.ohgrt.subscription.monthly"  // Plus
    static let yearlyProductId = "com.ohgrt.subscription.yearly"    // Pro

    static let monthlyPrice = "₹99"
    static let yearlyPrice = "₹799"
    static let yearlyMonthlyEquivalent = "₹67/mo"
    static let yearlySavings = "Save 33%"
}

// MARK: - Feature Categories for Display

struct FeatureCategory: Identifiable {
    let id = UUID()
    let name: String
    let icon: String
    let color: Color
    let features: [PremiumFeature]
}

let featureCategories: [FeatureCategory] = [
    FeatureCategory(
        name: "Chat & AI",
        icon: "bubble.left.and.bubble.right.fill",
        color: .purple,
        features: [.unlimitedMessages, .priorityResponse, .chatHistory, .voiceChat]
    ),
    FeatureCategory(
        name: "Astrology",
        icon: "sparkles",
        color: .orange,
        features: [.dailyHoroscope, .detailedKundli, .compatibility, .tarotReading, .panchang]
    ),
    FeatureCategory(
        name: "Travel",
        icon: "train.side.front.car",
        color: .blue,
        features: [.pnrStatus, .trainTracking, .multiPnr]
    ),
    FeatureCategory(
        name: "News & Info",
        icon: "newspaper.fill",
        color: .red,
        features: [.newsHeadlines, .personalizedNews, .weatherForecast, .cricketLiveScore]
    ),
    FeatureCategory(
        name: "Jobs & Career",
        icon: "briefcase.fill",
        color: .green,
        features: [.govtJobs, .jobAlerts, .resumeBuilder]
    ),
    FeatureCategory(
        name: "Premium Tools",
        icon: "crown.fill",
        color: .pink,
        features: [.aiImageGeneration, .documentScan, .adFree, .exportData, .customThemes]
    )
]

// MARK: - Comparison Table Data

struct TierComparison {
    let feature: PremiumFeature
    let freeValue: String
    let plusValue: String
    let proValue: String
}

let tierComparisons: [TierComparison] = [
    TierComparison(feature: .unlimitedMessages, freeValue: "10/day", plusValue: "100/day", proValue: "Unlimited"),
    TierComparison(feature: .dailyHoroscope, freeValue: "3/day", plusValue: "20/day", proValue: "Unlimited"),
    TierComparison(feature: .pnrStatus, freeValue: "5/day", plusValue: "20/day", proValue: "Unlimited"),
    TierComparison(feature: .aiImageGeneration, freeValue: "—", plusValue: "5/day", proValue: "50/day"),
    TierComparison(feature: .chatHistory, freeValue: "Today", plusValue: "30 days", proValue: "Forever"),
    TierComparison(feature: .adFree, freeValue: "—", plusValue: "✓", proValue: "✓"),
    TierComparison(feature: .priorityResponse, freeValue: "—", plusValue: "—", proValue: "✓"),
    TierComparison(feature: .customThemes, freeValue: "—", plusValue: "—", proValue: "✓"),
]
