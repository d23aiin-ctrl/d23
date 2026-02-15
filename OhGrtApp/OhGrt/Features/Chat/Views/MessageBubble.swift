import SwiftUI
import SwiftData
import UIKit

/// A single message bubble in the chat with animations
struct MessageBubble<M: DisplayableMessage>: View {
    let message: M
    var onRetry: (() -> Void)? = nil
    var onImageTap: ((URL) -> Void)? = nil

    @State private var appeared = false
    @State private var isPressed = false

    private var isUser: Bool {
        message.isUser
    }

    var body: some View {
        HStack(alignment: .bottom, spacing: 4) {
            if !isUser {
                assistantAvatar
            } else {
                Spacer(minLength: 0)
            }

            VStack(alignment: isUser ? .trailing : .leading, spacing: 6) {
                // Message content bubble
                messageBubble

                // Metadata row
                metadataRow
            }

            if isUser {
                userAvatar
            } else {
                Spacer(minLength: 4)
            }
        }
        .scaleEffect(appeared ? 1.0 : 0.8)
        .opacity(appeared ? 1.0 : 0)
        .offset(x: appeared ? 0 : (isUser ? 30 : -30))
        .onAppear {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                appeared = true
            }
        }
    }

    // MARK: - Components

    private var messageBubble: some View {
        let hasWeatherCard = !isUser && weatherCardData != nil
        let hasHoroscopeCard = !isUser && horoscopeCardData != nil
        let hasNewsCard = !isUser && newsCardData != nil
        let hasNumerologyCard = !isUser && numerologyCardData != nil
        let hasGovtJobsCard = !isUser && govtJobsCardData != nil
        let hasCricketCard = !isUser && cricketCardData != nil
        let hasTrainCard = !isUser && trainStatusCardData != nil
        let hasTarotCard = !isUser && tarotCardData != nil
        let hasPanchangCard = !isUser && panchangCardData != nil
        let hasPlacesCard = !isUser && placesCardData != nil
        let hasEmailListCard = !isUser && emailListCardData != nil
        let hasEmailComposeCard = !isUser && emailComposeCardData != nil
        let hasRichCard = hasWeatherCard || hasHoroscopeCard || hasNewsCard || hasNumerologyCard || hasGovtJobsCard || hasCricketCard || hasTrainCard || hasTarotCard || hasPanchangCard || hasPlacesCard || hasEmailListCard || hasEmailComposeCard
        return VStack(alignment: .leading, spacing: 8) {
            if let card = weatherCardData {
                WeatherCard(data: card)
            }

            if let card = horoscopeCardData {
                HoroscopeCard(data: card)
            }

            if let card = newsCardData {
                NewsCard(items: card.items, category: card.category)
            }

            if let card = numerologyCardData {
                NumerologyCard(data: card)
            }

            if let card = govtJobsCardData {
                GovtJobsCard(data: card)
            }

            if let card = cricketCardData {
                CricketScoreCard(data: card)
            }

            if let card = trainStatusCardData {
                TrainStatusCard(data: card)
            }

            if let card = tarotCardData {
                TarotCard(data: card)
            }

            if let card = panchangCardData {
                PanchangCard(data: card)
            }

            if let card = placesCardData {
                PlacesCard(data: card)
            }

            if let card = emailListCardData {
                EmailListChatCard(data: card)
            }

            if let card = emailComposeCardData {
                EmailComposeChatCard(data: card)
            }

            if let mediaView = mediaAttachment {
                mediaView
            }

            if !hasRichCard && !message.content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                messageTextView
                    .font(.body)
                    .lineSpacing(3)
                    .textSelection(.enabled)
            }
        }
        .padding(.horizontal, hasRichCard ? 0 : 12)
        .padding(.vertical, hasRichCard ? 0 : 10)
        .background(bubbleBackground.opacity(hasRichCard ? 0 : 1))
        .clipShape(RoundedCornerBubble(isUser: isUser))
        .frame(maxWidth: maxBubbleWidth, alignment: isUser ? .trailing : .leading)
        .shadow(
            color: hasRichCard ? Color.clear : Color.black.opacity(0.06),
            radius: 6,
            y: 2
        )
        .scaleEffect(isPressed ? 0.98 : 1.0)
        .contextMenu {
            Button(action: {
                UIPasteboard.general.string = message.content
                let feedback = UINotificationFeedbackGenerator()
                feedback.notificationOccurred(.success)
            }) {
                Label("Copy", systemImage: "doc.on.doc")
            }

            if let mediaURL = message.displayMediaURL, let url = URL(string: mediaURL) {
                Button(action: {
                    UIApplication.shared.open(url)
                }) {
                    Label("Open Attachment", systemImage: "link")
                }
            }

            if !isUser {
                Button(action: {
                    // Share action
                    let activityVC = UIActivityViewController(
                        activityItems: [message.content],
                        applicationActivities: nil
                    )
                    if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                       let window = windowScene.windows.first,
                       let rootVC = window.rootViewController {
                        rootVC.present(activityVC, animated: true)
                    }
                }) {
                    Label("Share", systemImage: "square.and.arrow.up")
                }
            }
        }
        .simultaneousGesture(
            LongPressGesture(minimumDuration: 0.2)
                .onChanged { _ in
                    withAnimation(.easeInOut(duration: 0.1)) {
                        isPressed = true
                    }
                }
                .onEnded { _ in
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                        isPressed = false
                    }
                }
        )
    }

    private var metadataRow: some View {
        HStack(spacing: 8) {
            // Category badge for assistant messages
            if !isUser, let category = message.displayCategory {
                categoryBadge(category)
            }

            // Timestamp
            Text(message.createdAt, style: .time)
                .font(.caption2)
                .foregroundColor(.secondary)

            // Status indicator for user messages
            if isUser {
                statusIndicator
            }

            // Sync status / retry for user messages
            if isUser && !message.displaySynced {
                retryButton
            }
        }
    }

    private func categoryBadge(_ category: String) -> some View {
        HStack(spacing: 4) {
            Image(systemName: categoryIcon(for: category))
                .font(.system(size: 9))
            Text(category.capitalized)
                .font(.caption2)
                .fontWeight(.medium)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(
            Capsule()
                .fill(categoryColor(for: category).opacity(0.12))
        )
        .foregroundColor(categoryColor(for: category))
    }

    private var statusIndicator: some View {
        Group {
            if message.displaySynced {
                Image(systemName: "checkmark")
                    .font(.system(size: 10, weight: .semibold))
                    .foregroundColor(.secondary)
            }
        }
    }

    private var retryButton: some View {
        Button(action: {
            let feedback = UIImpactFeedbackGenerator(style: .medium)
            feedback.impactOccurred()
            onRetry?()
        }) {
            HStack(spacing: 4) {
                Image(systemName: "exclamationmark.circle.fill")
                    .font(.system(size: 12))
                Text("Retry")
                    .font(.caption2)
                    .fontWeight(.medium)
            }
            .foregroundColor(.orange)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(Color.orange.opacity(0.12))
            )
        }
    }

    @ViewBuilder
    private var bubbleBackground: some View {
        if isUser {
            LinearGradient(
                colors: [
                    Color(red: 0.72, green: 0.35, blue: 0.94),
                    Color(red: 0.55, green: 0.18, blue: 0.85)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        } else {
            LinearGradient(
                colors: [
                    Color(red: 0.16, green: 0.12, blue: 0.2),
                    Color(red: 0.12, green: 0.1, blue: 0.16)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }

    // MARK: - Helpers

    private func categoryIcon(for category: String) -> String {
        switch category.lowercased() {
        case "horoscope", "astrology", "kundli", "zodiac": return "sparkles"
        case "weather": return "cloud.sun.fill"
        case "news": return "newspaper.fill"
        case "pnr", "train", "travel": return "train.side.front.car"
        case "tarot": return "suit.diamond.fill"
        case "numerology": return "number.circle.fill"
        case "panchang": return "calendar"
        case "government", "govt": return "building.columns.fill"
        case "food": return "fork.knife.circle.fill"
        case "games": return "puzzlepiece.extension.fill"
        case "reminder": return "bell.fill"
        case "email", "gmail", "email_list", "email_compose", "email_send": return "envelope.fill"
        default: return "bubble.left.fill"
        }
    }

    private func categoryColor(for category: String) -> Color {
        switch category.lowercased() {
        case "horoscope", "astrology", "kundli", "zodiac": return .purple
        case "weather": return .cyan
        case "news": return .red
        case "pnr", "train", "travel": return .blue
        case "tarot": return .indigo
        case "numerology": return .orange
        case "panchang": return .teal
        case "government", "govt": return .blue
        case "food": return .orange
        case "games": return .pink
        case "reminder": return .orange
        case "email", "gmail", "email_list", "email_compose", "email_send": return .blue
        default: return .blue
        }
    }

    private var mediaAttachment: AnyView? {
        guard let mediaURL = message.displayMediaURL,
              let url = URL(string: mediaURL) else {
            return nil
        }

        if isImageURL(url) {
            return AnyView(
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .empty:
                        ZStack {
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color(.systemGray5))
                            ProgressView()
                        }
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    case .failure:
                        attachmentLinkView(url: url, label: "Image attachment")
                    @unknown default:
                        attachmentLinkView(url: url, label: "Image attachment")
                    }
                }
                .frame(maxWidth: 220, maxHeight: 180)
                .clipped()
                .cornerRadius(12)
                .onTapGesture {
                    onImageTap?(url)
                }
            )
        }

        return AnyView(attachmentLinkView(url: url, label: attachmentLabel(for: url)))
    }

    private var messageTextView: Text {
        Text(messageAttributedString(from: message.content))
    }

    private func messageAttributedString(from text: String) -> AttributedString {
        let baseColor: Color = isUser ? .white : Color(red: 0.9, green: 0.88, blue: 0.95)
        let linkColor: Color = isUser ? .white.opacity(0.95) : Color(red: 0.6, green: 0.78, blue: 1.0)
        var attributed = (try? AttributedString(markdown: text)) ?? AttributedString(text)
        attributed.foregroundColor = baseColor
        applyLinkAttributes(
            to: &attributed,
            in: text,
            linkColor: linkColor
        )
        return attributed
    }

    private func applyLinkAttributes(
        to attributed: inout AttributedString,
        in text: String,
        linkColor: Color
    ) {
        guard let detector = try? NSDataDetector(types: NSTextCheckingResult.CheckingType.link.rawValue) else {
            return
        }

        let matches = detector.matches(
            in: text,
            options: [],
            range: NSRange(text.startIndex..<text.endIndex, in: text)
        )
        guard !matches.isEmpty else { return }
        for match in matches {
            guard let url = match.url,
                  let range = Range(match.range, in: text),
                  let attributedRange = Range(range, in: attributed) else {
                continue
            }
            attributed[attributedRange].link = url
            attributed[attributedRange].foregroundColor = linkColor
            attributed[attributedRange].underlineStyle = .single
        }
    }

    private var maxBubbleWidth: CGFloat {
        UIScreen.main.bounds.width * 0.98
    }

    private var weatherCardData: WeatherCardData? {
        if let data = weatherCardDataFromStructuredJSON() {
            return data
        }

        guard !isUser else { return nil }
        let category = message.displayCategory?.lowercased() ?? ""
        let content = message.content
        if category == "weather"
            || content.lowercased().contains("weather")
            || content.lowercased().contains("temperature")
            || content.lowercased().contains("humidity") {
            return weatherCardDataFromText(content)
        }
        return nil
    }

    private var horoscopeCardData: HoroscopeCardData? {
        guard !isUser else { return nil }
        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object
        guard let sign = stringValue(dataObject["sign"] ?? dataObject["zodiac_sign"]) else {
            return nil
        }

        let horoscope = stringValue(
            dataObject["horoscope"]
                ?? dataObject["daily_horoscope"]
                ?? dataObject["description"]
        ) ?? ""
        let period = stringValue(dataObject["period"] ?? dataObject["date"]) ?? "Today"

        return HoroscopeCardData(
            sign: sign,
            period: period,
            horoscope: horoscope,
            luckyNumber: stringValue(dataObject["lucky_number"] ?? dataObject["luckyNumber"]),
            luckyColor: stringValue(dataObject["lucky_color"] ?? dataObject["luckyColor"]),
            mood: stringValue(dataObject["mood"]),
            compatibility: stringValue(dataObject["compatibility"]),
            focusArea: stringValue(dataObject["focus_area"] ?? dataObject["focusArea"]),
            advice: stringValue(dataObject["advice"])
        )
    }

    private var newsCardData: NewsCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "news" && category != "get_news" && category != "headline" {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        let items = extractNewsItems(from: dataObject)
        guard !items.isEmpty else { return nil }

        let headlineCategory = stringValue(dataObject["category"] ?? dataObject["news_category"])
        return NewsCardData(items: items, category: headlineCategory)
    }

    private var numerologyCardData: NumerologyCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "numerology" {
            return nil
        }
        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        let name = stringValue(dataObject["name"]) ?? "Numerology"
        let nameNumber = stringValue(dataObject["name_number"] ?? dataObject["nameNumber"])
        let lifePath = stringValue(dataObject["life_path_number"] ?? dataObject["lifePathNumber"])
        let expression = stringValue(dataObject["expression_number"] ?? dataObject["expressionNumber"])
        let soulUrge = stringValue(dataObject["soul_urge_number"] ?? dataObject["soulUrgeNumber"])
        let personality = stringValue(dataObject["personality_number"] ?? dataObject["personalityNumber"])

        let nameMeaning = dataObject["name_meaning"] as? [String: Any]
        let lifePathMeaning = dataObject["life_path_meaning"] as? [String: Any]

        let luckyNumbers = dataObject["lucky_numbers"] as? [Any] ?? []
        let luckyNumberText = luckyNumbers.compactMap { stringValue($0) }

        return NumerologyCardData(
            name: name,
            nameNumber: nameNumber,
            nameTrait: stringValue(nameMeaning?["trait"]),
            nameDescription: stringValue(nameMeaning?["description"]),
            lifePathNumber: lifePath,
            lifePathTrait: stringValue(lifePathMeaning?["trait"]),
            expressionNumber: expression,
            soulUrgeNumber: soulUrge,
            personalityNumber: personality,
            luckyNumbers: luckyNumberText
        )
    }

    private var govtJobsCardData: GovtJobsCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "govt_jobs" && category != "government_jobs" && category != "sarkari_naukri" && category != "jobs" {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        let items = extractGovtJobItems(from: dataObject)
        guard !items.isEmpty else { return nil }

        let searchQuery = stringValue(dataObject["query"] ?? dataObject["search_query"])
        let totalJobs = dataObject["total_jobs"] as? Int ?? items.count
        let totalVacancies = dataObject["total_vacancies"] as? Int
        let date = stringValue(dataObject["date"])

        return GovtJobsCardData(
            items: items,
            searchQuery: searchQuery,
            totalJobs: totalJobs,
            totalVacancies: totalVacancies,
            date: date
        )
    }

    private var placesCardData: PlacesCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if !["food", "local_search", "nearby", "local", "restaurants", "restaurant"].contains(category) {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object
        let items = extractPlaceItems(from: dataObject)
        guard !items.isEmpty else { return nil }

        let query = stringValue(dataObject["query"] ?? dataObject["search_query"])
        let location = stringValue(dataObject["location"] ?? dataObject["city"] ?? dataObject["area"])

        return PlacesCardData(
            title: category == "food" ? "Restaurants" : "Nearby Places",
            query: query,
            location: location,
            items: items
        )
    }

    // MARK: - Email Cards

    private var emailListCardData: EmailListCardData? {
        guard !isUser else { return nil }
        guard let object = structuredDataObject() else { return nil }
        guard stringValue(object["type"]) == "email_list" else { return nil }

        guard let emailsArray = object["emails"] as? [[String: Any]] else { return nil }
        let items = emailsArray.compactMap { dict -> EmailListItem? in
            guard let id = stringValue(dict["id"]),
                  let subject = stringValue(dict["subject"]) else { return nil }
            return EmailListItem(
                id: id,
                subject: subject,
                from: stringValue(dict["from"]) ?? "",
                date: stringValue(dict["date"]) ?? "",
                snippet: stringValue(dict["snippet"]) ?? ""
            )
        }
        guard !items.isEmpty else { return nil }
        let count = intValue(object["count"]) ?? items.count
        return EmailListCardData(emails: items, count: count)
    }

    private var emailComposeCardData: EmailComposeCardData? {
        guard !isUser else { return nil }
        guard let object = structuredDataObject() else { return nil }
        guard stringValue(object["type"]) == "email_compose" else { return nil }

        return EmailComposeCardData(
            to: stringValue(object["to"]) ?? "",
            subject: stringValue(object["subject"]) ?? "",
            body: stringValue(object["body"]) ?? "",
            cc: stringValue(object["cc"]),
            bcc: stringValue(object["bcc"])
        )
    }

    private func extractPlaceItems(from object: [String: Any]) -> [PlaceItem] {
        let containers: [Any?] = [
            object["places"],
            object["results"],
            object["items"],
            object["businesses"],
            object["locations"],
            object["data"]
        ]

        for container in containers {
            if let items = container as? [[String: Any]] {
                let mapped = items.compactMap { mapPlaceItem($0) }
                if !mapped.isEmpty {
                    return mapped
                }
            }
        }

        if let single = mapPlaceItem(object) {
            return [single]
        }
        return []
    }

    private func mapPlaceItem(_ object: [String: Any]) -> PlaceItem? {
        let name = stringValue(object["name"] ?? object["title"])
        guard let placeName = name, !placeName.isEmpty else { return nil }

        let address = stringValue(
            object["address"]
                ?? object["vicinity"]
                ?? object["formatted_address"]
                ?? object["location"]
        )

        let rating = doubleValue(object["rating"])
        let reviewCount = intValue(object["reviews"] ?? object["review_count"] ?? object["user_ratings_total"])
        let price = stringValue(object["price"] ?? object["price_level"])
        let distance = stringValue(
            object["distance"]
                ?? object["distance_text"]
                ?? object["distance_km"]
                ?? object["distance_m"]
        )
        let isOpen = boolValue(object["open_now"] ?? object["is_open"])
        let url = stringValue(object["url"] ?? object["website"])
        let imageURL = stringValue(object["image_url"] ?? object["photo"] ?? object["image"])

        return PlaceItem(
            name: placeName,
            address: address,
            rating: rating,
            reviewCount: reviewCount,
            price: price,
            distance: distance,
            isOpen: isOpen,
            url: url,
            imageURL: imageURL
        )
    }

    private var cricketCardData: CricketScoreCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "cricket" && category != "cricket_score" && category != "get_cricket_score" && category != "live_score" {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        guard let team1 = stringValue(dataObject["team1"] ?? dataObject["team_1"] ?? dataObject["batting_team"]),
              let score1 = stringValue(dataObject["score1"] ?? dataObject["score_1"] ?? dataObject["batting_score"]) else {
            return nil
        }

        let team2 = stringValue(dataObject["team2"] ?? dataObject["team_2"] ?? dataObject["bowling_team"]) ?? "TBD"

        return CricketScoreCardData(
            team1: team1,
            team2: team2,
            score1: score1,
            score2: stringValue(dataObject["score2"] ?? dataObject["score_2"] ?? dataObject["bowling_score"]),
            overs1: stringValue(dataObject["overs1"] ?? dataObject["overs_1"] ?? dataObject["batting_overs"]),
            overs2: stringValue(dataObject["overs2"] ?? dataObject["overs_2"] ?? dataObject["bowling_overs"]),
            status: stringValue(dataObject["status"] ?? dataObject["match_status"]) ?? "In Progress",
            venue: stringValue(dataObject["venue"] ?? dataObject["stadium"]),
            matchType: stringValue(dataObject["match_type"] ?? dataObject["format"]),
            currentBatsman: stringValue(dataObject["current_batsman"] ?? dataObject["batsman"]),
            currentBowler: stringValue(dataObject["current_bowler"] ?? dataObject["bowler"]),
            runRate: stringValue(dataObject["run_rate"] ?? dataObject["crr"]),
            requiredRunRate: stringValue(dataObject["required_run_rate"] ?? dataObject["rrr"]),
            target: stringValue(dataObject["target"]),
            isLive: (dataObject["is_live"] as? Bool) ?? (dataObject["live"] as? Bool) ?? true
        )
    }

    private var trainStatusCardData: TrainStatusCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "pnr" && category != "train" && category != "train_status" && category != "pnr_status" && category != "get_pnr_status" && category != "get_train_status" {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        guard let trainNumber = stringValue(dataObject["train_number"] ?? dataObject["trainNumber"] ?? dataObject["train_no"]) else {
            return nil
        }

        let passengers = extractPassengers(from: dataObject)

        return TrainStatusCardData(
            pnr: stringValue(dataObject["pnr"] ?? dataObject["pnr_number"]),
            trainNumber: trainNumber,
            trainName: stringValue(dataObject["train_name"] ?? dataObject["trainName"]) ?? "Express",
            fromStation: stringValue(dataObject["from_station"] ?? dataObject["source"] ?? dataObject["from"]) ?? "Source",
            toStation: stringValue(dataObject["to_station"] ?? dataObject["destination"] ?? dataObject["to"]) ?? "Destination",
            departureTime: stringValue(dataObject["departure_time"] ?? dataObject["departure"]),
            arrivalTime: stringValue(dataObject["arrival_time"] ?? dataObject["arrival"]),
            date: stringValue(dataObject["date"] ?? dataObject["journey_date"]),
            status: stringValue(dataObject["status"] ?? dataObject["booking_status"]) ?? "Status Unknown",
            delay: stringValue(dataObject["delay"] ?? dataObject["late_by"]),
            coach: stringValue(dataObject["coach"]),
            berth: stringValue(dataObject["berth"] ?? dataObject["seat"]),
            passengers: passengers,
            currentStation: stringValue(dataObject["current_station"] ?? dataObject["current_location"]),
            lastUpdated: stringValue(dataObject["last_updated"] ?? dataObject["updated_at"]),
            isLive: (dataObject["is_live"] as? Bool) ?? false
        )
    }

    private func extractPassengers(from object: [String: Any]) -> [PassengerInfo] {
        let containers: [Any?] = [
            object["passengers"],
            object["passenger_list"],
            object["pax"]
        ]

        for container in containers {
            if let items = container as? [[String: Any]] {
                return items.compactMap { mapPassenger($0) }
            }
        }
        return []
    }

    private func mapPassenger(_ object: [String: Any]) -> PassengerInfo? {
        let seat = stringValue(object["seat"] ?? object["berth"] ?? object["current_status"])
        if seat == nil { return nil }

        return PassengerInfo(
            name: stringValue(object["name"] ?? object["passenger_name"]),
            seat: seat ?? "—",
            status: stringValue(object["status"] ?? object["booking_status"]) ?? "—",
            coach: stringValue(object["coach"])
        )
    }

    private var tarotCardData: TarotCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "tarot" && category != "tarot_reading" && category != "get_tarot" {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        guard let cardName = stringValue(dataObject["card_name"] ?? dataObject["cardName"] ?? dataObject["name"]) else {
            return nil
        }

        let keywordsRaw = dataObject["keywords"] as? [Any] ?? []
        let keywords = keywordsRaw.compactMap { stringValue($0) }

        return TarotCardData(
            cardName: cardName,
            cardNumber: stringValue(dataObject["card_number"] ?? dataObject["number"]),
            meaning: stringValue(dataObject["meaning"] ?? dataObject["description"]) ?? "",
            interpretation: stringValue(dataObject["interpretation"] ?? dataObject["reading"]),
            advice: stringValue(dataObject["advice"] ?? dataObject["guidance"]),
            isReversed: (dataObject["is_reversed"] as? Bool) ?? (dataObject["reversed"] as? Bool) ?? false,
            suit: stringValue(dataObject["suit"] ?? dataObject["arcana"]),
            element: stringValue(dataObject["element"]),
            keywords: keywords
        )
    }

    private var panchangCardData: PanchangCardData? {
        guard !isUser else { return nil }
        let category = (message.displayCategory ?? "").lowercased()
        if category != "panchang" && category != "get_panchang" && category != "hindu_calendar" {
            return nil
        }

        guard let object = structuredDataObject() else { return nil }
        let dataObject = (object["data"] as? [String: Any]) ?? object

        guard let tithi = stringValue(dataObject["tithi"]),
              let nakshatra = stringValue(dataObject["nakshatra"]) else {
            return nil
        }

        return PanchangCardData(
            date: stringValue(dataObject["date"]) ?? "Today",
            day: stringValue(dataObject["day"] ?? dataObject["weekday"]) ?? "",
            tithi: tithi,
            nakshatra: nakshatra,
            yoga: stringValue(dataObject["yoga"]),
            karana: stringValue(dataObject["karana"]),
            sunrise: stringValue(dataObject["sunrise"]),
            sunset: stringValue(dataObject["sunset"]),
            moonrise: stringValue(dataObject["moonrise"]),
            moonset: stringValue(dataObject["moonset"]),
            rahukaal: stringValue(dataObject["rahukaal"] ?? dataObject["rahu_kaal"]),
            auspiciousTime: stringValue(dataObject["auspicious_time"] ?? dataObject["shubh_muhurat"]),
            inauspiciousTime: stringValue(dataObject["inauspicious_time"]),
            festival: stringValue(dataObject["festival"] ?? dataObject["holiday"]),
            masa: stringValue(dataObject["masa"] ?? dataObject["month"]),
            paksha: stringValue(dataObject["paksha"])
        )
    }

    private func extractGovtJobItems(from object: [String: Any]) -> [GovtJobItem] {
        let containers: [Any?] = [
            object["jobs"],
            object["items"],
            object["results"],
            object["data"]
        ]

        for container in containers {
            if let items = container as? [[String: Any]] {
                return items.compactMap { mapGovtJobItem($0) }
            }
        }

        if let single = mapGovtJobItem(object) {
            return [single]
        }
        return []
    }

    private func mapGovtJobItem(_ object: [String: Any]) -> GovtJobItem? {
        let title = stringValue(object["title"] ?? object["post_name"] ?? object["job_title"])
        if title == nil { return nil }
        return GovtJobItem(
            title: title ?? "",
            organization: stringValue(object["organization"] ?? object["department"] ?? object["org"]),
            vacancies: stringValue(object["vacancies"] ?? object["total_vacancies"] ?? object["posts"]),
            lastDate: stringValue(object["last_date"] ?? object["lastDate"] ?? object["apply_before"]),
            qualification: stringValue(object["qualification"] ?? object["eligibility"]),
            salary: stringValue(object["salary"] ?? object["pay_scale"]),
            location: stringValue(object["location"] ?? object["place"]),
            url: stringValue(object["url"] ?? object["apply_link"] ?? object["link"]),
            isNew: (object["is_new"] as? Bool) ?? false,
            snippet: stringValue(object["snippet"] ?? object["description"])
        )
    }

    private func extractNewsItems(from object: [String: Any]) -> [NewsItem] {
        let containers: [Any?] = [
            object["articles"],
            object["items"],
            object["news"],
            object["data"]
        ]

        for container in containers {
            if let items = container as? [[String: Any]] {
                return items.compactMap { mapNewsItem($0) }
            }
        }

        if let single = mapNewsItem(object) {
            return [single]
        }
        return []
    }

    private func mapNewsItem(_ object: [String: Any]) -> NewsItem? {
        let title = stringValue(object["title"] ?? object["headline"])
        if title == nil { return nil }
        return NewsItem(
            title: title ?? "",
            summary: stringValue(object["summary"] ?? object["description"]),
            source: stringValue(object["source"]),
            url: stringValue(object["url"]),
            publishedAt: stringValue(object["published_at"] ?? object["publishedAt"]),
            imageURL: stringValue(object["image_url"] ?? object["imageUrl"]),
            category: stringValue(object["category"])
        )
    }

    private func structuredDataObject() -> [String: Any]? {
        guard let json = message.displayStructuredDataJSON,
              let data = json.data(using: .utf8),
              let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        return object
    }

    private func weatherCardDataFromStructuredJSON() -> WeatherCardData? {
        guard let object = structuredDataObject(),
              let temp = doubleValue(object["temperature"] ?? object["temperature_c"]) else {
            return nil
        }

        let city = object["city"] as? String ?? "Unknown"
        let humidity = doubleValue(object["humidity"]) ?? 0
        let condition = object["condition"] as? String ?? "—"

        var windSpeed: Double?
        var visibilityKm: Double?

        if let raw = object["raw"] as? [String: Any] {
            if let wind = raw["wind"] as? [String: Any] {
                windSpeed = doubleValue(wind["speed"])
            }
            if let visibility = raw["visibility"] as? Double {
                visibilityKm = visibility / 1000.0
            } else if let visibility = raw["visibility"] as? Int {
                visibilityKm = Double(visibility) / 1000.0
            }
        }

        return WeatherCardData(
            city: city,
            temperature: temp,
            condition: condition,
            humidity: humidity,
            windSpeed: windSpeed,
            visibilityKm: visibilityKm
        )
    }

    private func weatherCardDataFromText(_ text: String) -> WeatherCardData? {
        let city = firstMatch(
            pattern: "(?i)weather\\s+in\\s+([^|\\n]+)",
            text: text
        )
            ?? firstMatch(
                pattern: "(?i)weather\\s+(?:for|in)\\s+([^:\\n]+)",
                text: text
            )
            ?? "Unknown"

        let temp = firstDoubleMatch(
            pattern: "(?i)temperature[^0-9]*([0-9]+(?:\\.[0-9]+)?)\\s*°?c",
            text: text
        )
            ?? firstDoubleMatch(pattern: "([0-9]+(?:\\.[0-9]+)?)\\s*°c", text: text)
        guard let temperature = temp else { return nil }

        let humidity = firstDoubleMatch(
            pattern: "(?i)humidity[^0-9]*([0-9]+(?:\\.[0-9]+)?)",
            text: text
        ) ?? 0
        let condition = firstMatch(
            pattern: "\\|\\s*([^|]+)\\s*temperature",
            text: text
        )
            ?? firstMatch(pattern: "(?i)condition[:\\s]*([A-Za-z\\s]+)", text: text)
            ?? firstMatch(pattern: "(?i)\\n?([A-Za-z\\s]+)\\s*\\n?feels like", text: text)
            ?? "—"
        let wind = firstDoubleMatch(
            pattern: "(?i)wind[^0-9]*([0-9]+(?:\\.[0-9]+)?)\\s*m/s",
            text: text
        )
        let visibility = firstDoubleMatch(
            pattern: "(?i)visibility[^0-9]*([0-9]+(?:\\.[0-9]+)?)\\s*km",
            text: text
        )

        return WeatherCardData(
            city: city.replacingOccurrences(of: "  ", with: " ").trimmingCharacters(in: .whitespacesAndNewlines),
            temperature: temperature,
            condition: condition.trimmingCharacters(in: .whitespacesAndNewlines),
            humidity: humidity,
            windSpeed: wind,
            visibilityKm: visibility
        )
    }

    private func firstDoubleMatch(pattern: String, text: String) -> Double? {
        guard let match = firstMatch(pattern: pattern, text: text) else { return nil }
        return Double(match)
    }

    private func firstMatch(pattern: String, text: String) -> String? {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else { return nil }
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        guard let match = regex.firstMatch(in: text, options: [], range: range),
              match.numberOfRanges > 1,
              let matchRange = Range(match.range(at: 1), in: text) else { return nil }
        return String(text[matchRange])
    }

    private func stringValue(_ value: Any?) -> String? {
        switch value {
        case let string as String:
            return string
        case let number as Double:
            return String(number)
        case let number as Int:
            return String(number)
        default:
            return nil
        }
    }

    private func doubleValue(_ value: Any?) -> Double? {
        switch value {
        case let number as Double:
            return number
        case let number as Int:
            return Double(number)
        case let number as Float:
            return Double(number)
        case let string as String:
            return Double(string)
        default:
            return nil
        }
    }

    private func intValue(_ value: Any?) -> Int? {
        switch value {
        case let number as Int:
            return number
        case let number as Double:
            return Int(number)
        case let number as Float:
            return Int(number)
        case let string as String:
            return Int(string)
        default:
            return nil
        }
    }

    private func boolValue(_ value: Any?) -> Bool? {
        switch value {
        case let bool as Bool:
            return bool
        case let number as Int:
            return number != 0
        case let string as String:
            return ["true", "yes", "1", "open"].contains(string.lowercased())
        default:
            return nil
        }
    }

    private var assistantAvatar: some View {
        ZStack {
            Circle()
                .fill(Color(red: 0.14, green: 0.11, blue: 0.18))
                .frame(width: 30, height: 30)
            Image(systemName: "sparkles")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(Color(red: 0.78, green: 0.72, blue: 0.9))
        }
    }

    private var userAvatar: some View {
        ZStack {
            Circle()
                .fill(Color(red: 0.72, green: 0.35, blue: 0.94))
                .frame(width: 30, height: 30)
            Image(systemName: "person.fill")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white)
        }
    }

    private func attachmentLabel(for url: URL) -> String {
        if isAudioURL(url) {
            return "Audio attachment"
        }
        if isVideoURL(url) {
            return "Video attachment"
        }
        return "File attachment"
    }

    private func attachmentLinkView(url: URL, label: String) -> some View {
        Link(destination: url) {
            HStack(spacing: 8) {
                Image(systemName: attachmentIcon(for: url))
                    .font(.system(size: 14, weight: .semibold))
                Text(label)
                    .font(.caption)
                    .fontWeight(.semibold)
            }
            .foregroundColor(isUser ? .white : .primary)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(isUser ? Color.white.opacity(0.2) : Color.black.opacity(0.06))
            )
        }
    }

    private func attachmentIcon(for url: URL) -> String {
        if isAudioURL(url) {
            return "waveform"
        }
        if isVideoURL(url) {
            return "play.rectangle.fill"
        }
        return "paperclip"
    }

    private func isImageURL(_ url: URL) -> Bool {
        let ext = url.pathExtension.lowercased()
        return ["jpg", "jpeg", "png", "gif", "webp", "heic"].contains(ext)
    }

    private func isAudioURL(_ url: URL) -> Bool {
        let ext = url.pathExtension.lowercased()
        return ["mp3", "m4a", "aac", "wav", "ogg"].contains(ext)
    }

    private func isVideoURL(_ url: URL) -> Bool {
        let ext = url.pathExtension.lowercased()
        return ["mp4", "mov", "m4v"].contains(ext)
    }
}

// MARK: - Full Screen Image Viewer

// MARK: - Custom Bubble Shape

struct RoundedCornerBubble: Shape {
    let isUser: Bool

    func path(in rect: CGRect) -> Path {
        let large: CGFloat = 18
        let small: CGFloat = 6
        let radii = isUser
            ? RectangleCornerRadii(
                topLeading: large,
                bottomLeading: large,
                bottomTrailing: large,
                topTrailing: small
            )
            : RectangleCornerRadii(
                topLeading: small,
                bottomLeading: large,
                bottomTrailing: large,
                topTrailing: large
            )
        return Path(roundedRect: rect, cornerRadii: radii)
    }
}

private struct WeatherCardData: Equatable {
    let city: String
    let temperature: Double
    let condition: String
    let humidity: Double
    let windSpeed: Double?
    let visibilityKm: Double?
}

// MARK: - Cricket Score Card

private struct CricketScoreCardData: Equatable {
    let team1: String
    let team2: String
    let score1: String
    let score2: String?
    let overs1: String?
    let overs2: String?
    let status: String
    let venue: String?
    let matchType: String?
    let currentBatsman: String?
    let currentBowler: String?
    let runRate: String?
    let requiredRunRate: String?
    let target: String?
    let isLive: Bool
}

private struct CricketScoreCard: View {
    let data: CricketScoreCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            scoreSection
            if data.currentBatsman != nil || data.currentBowler != nil {
                playersSection
            }
            statusFooter
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.05, green: 0.12, blue: 0.08),
                    Color(red: 0.02, green: 0.06, blue: 0.04)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(
                    LinearGradient(
                        colors: [Color.green.opacity(0.4), Color.teal.opacity(0.2)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
        )
        .shadow(color: Color.black.opacity(0.45), radius: 20, y: 10)
    }

    private var header: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.green, Color.teal],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 42, height: 42)
                    .shadow(color: Color.green.opacity(0.4), radius: 8, y: 4)

                Image(systemName: "sportscourt.fill")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(data.matchType ?? "CRICKET")
                        .font(.caption)
                        .fontWeight(.heavy)
                        .foregroundColor(Color.green.opacity(0.9))
                        .tracking(1)

                    if data.isLive {
                        HStack(spacing: 4) {
                            Circle()
                                .fill(Color.red)
                                .frame(width: 6, height: 6)
                            Text("LIVE")
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.red)
                        }
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(Color.red.opacity(0.15))
                        .clipShape(Capsule())
                    }
                }

                if let venue = data.venue {
                    Text(venue)
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                        .lineLimit(1)
                }
            }

            Spacer()
        }
        .padding(16)
        .background(
            LinearGradient(
                colors: [
                    Color.green.opacity(0.2),
                    Color.teal.opacity(0.08),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var scoreSection: some View {
        VStack(spacing: 16) {
            // Team 1
            HStack {
                TeamFlag(teamName: data.team1)

                VStack(alignment: .leading, spacing: 2) {
                    Text(data.team1)
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundColor(.white)

                    if let overs = data.overs1 {
                        Text("(\(overs) ov)")
                            .font(.caption2)
                            .foregroundColor(Color.white.opacity(0.5))
                    }
                }

                Spacer()

                Text(data.score1)
                    .font(.title2)
                    .fontWeight(.heavy)
                    .foregroundColor(.white)
            }

            // Divider with optional target
            HStack {
                Rectangle()
                    .fill(Color.white.opacity(0.1))
                    .frame(height: 1)

                if let target = data.target {
                    Text("Target: \(target)")
                        .font(.caption2)
                        .foregroundColor(Color.orange)
                        .padding(.horizontal, 8)
                }

                Rectangle()
                    .fill(Color.white.opacity(0.1))
                    .frame(height: 1)
            }

            // Team 2
            if let score2 = data.score2 {
                HStack {
                    TeamFlag(teamName: data.team2)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(data.team2)
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(.white)

                        if let overs = data.overs2 {
                            Text("(\(overs) ov)")
                                .font(.caption2)
                                .foregroundColor(Color.white.opacity(0.5))
                        }
                    }

                    Spacer()

                    Text(score2)
                        .font(.title2)
                        .fontWeight(.heavy)
                        .foregroundColor(.white)
                }
            } else {
                HStack {
                    TeamFlag(teamName: data.team2)

                    Text(data.team2)
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundColor(Color.white.opacity(0.6))

                    Spacer()

                    Text("Yet to bat")
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.4))
                }
            }

            // Run Rate Info
            if data.runRate != nil || data.requiredRunRate != nil {
                HStack(spacing: 16) {
                    if let crr = data.runRate {
                        CricketStatPill(label: "CRR", value: crr, color: .cyan)
                    }
                    if let rrr = data.requiredRunRate {
                        CricketStatPill(label: "RRR", value: rrr, color: .orange)
                    }
                }
            }
        }
        .padding(16)
    }

    private var playersSection: some View {
        VStack(spacing: 8) {
            if let batsman = data.currentBatsman {
                HStack(spacing: 8) {
                    Image(systemName: "figure.cricket")
                        .font(.caption)
                        .foregroundColor(Color.green)
                    Text("Batting:")
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                    Text(batsman)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                    Spacer()
                }
            }

            if let bowler = data.currentBowler {
                HStack(spacing: 8) {
                    Image(systemName: "circle.fill")
                        .font(.system(size: 6))
                        .foregroundColor(Color.red.opacity(0.8))
                    Text("Bowling:")
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                    Text(bowler)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                    Spacer()
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }

    private var statusFooter: some View {
        HStack {
            Image(systemName: data.isLive ? "antenna.radiowaves.left.and.right" : "clock")
                .font(.caption)
                .foregroundColor(data.isLive ? Color.green : Color.white.opacity(0.5))

            Text(data.status)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.white)

            Spacer()
        }
        .padding(12)
        .background(Color.black.opacity(0.3))
    }
}

private struct TeamFlag: View {
    let teamName: String

    var body: some View {
        ZStack {
            Circle()
                .fill(teamColor.opacity(0.2))
                .frame(width: 36, height: 36)

            Text(teamInitials)
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(teamColor)
        }
    }

    private var teamInitials: String {
        let words = teamName.split(separator: " ")
        if words.count >= 2 {
            return String(words[0].prefix(1) + words[1].prefix(1)).uppercased()
        }
        return String(teamName.prefix(2)).uppercased()
    }

    private var teamColor: Color {
        let name = teamName.lowercased()
        if name.contains("india") || name.contains("ind") { return .blue }
        if name.contains("australia") || name.contains("aus") { return .yellow }
        if name.contains("england") || name.contains("eng") { return .red }
        if name.contains("pakistan") || name.contains("pak") { return .green }
        if name.contains("south africa") || name.contains("sa") { return .green }
        if name.contains("new zealand") || name.contains("nz") { return .cyan }
        if name.contains("west indies") || name.contains("wi") { return .purple }
        if name.contains("sri lanka") || name.contains("sl") { return .blue }
        if name.contains("bangladesh") || name.contains("ban") { return .green }
        if name.contains("csk") || name.contains("chennai") { return .yellow }
        if name.contains("mi") || name.contains("mumbai") { return .blue }
        if name.contains("rcb") || name.contains("bangalore") { return .red }
        if name.contains("kkr") || name.contains("kolkata") { return .purple }
        if name.contains("dc") || name.contains("delhi") { return .blue }
        if name.contains("srh") || name.contains("hyderabad") { return .orange }
        if name.contains("rr") || name.contains("rajasthan") { return .pink }
        if name.contains("pbks") || name.contains("punjab") { return .red }
        if name.contains("gt") || name.contains("gujarat") { return .cyan }
        if name.contains("lsg") || name.contains("lucknow") { return .cyan }
        return .white
    }
}

private struct CricketStatPill: View {
    let label: String
    let value: String
    let color: Color

    var body: some View {
        HStack(spacing: 4) {
            Text(label)
                .font(.caption2)
                .foregroundColor(Color.white.opacity(0.5))
            Text(value)
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(Color.white.opacity(0.08))
        .clipShape(Capsule())
    }
}

// MARK: - PNR/Train Status Card

private struct TrainStatusCardData: Equatable {
    let pnr: String?
    let trainNumber: String
    let trainName: String
    let fromStation: String
    let toStation: String
    let departureTime: String?
    let arrivalTime: String?
    let date: String?
    let status: String
    let delay: String?
    let coach: String?
    let berth: String?
    let passengers: [PassengerInfo]
    let currentStation: String?
    let lastUpdated: String?
    let isLive: Bool
}

private struct PassengerInfo: Equatable {
    let name: String?
    let seat: String
    let status: String
    let coach: String?
}

private struct TrainStatusCard: View {
    let data: TrainStatusCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            journeySection
            if !data.passengers.isEmpty {
                passengersSection
            }
            statusFooter
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.06, green: 0.08, blue: 0.14),
                    Color(red: 0.03, green: 0.04, blue: 0.08)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(
                    LinearGradient(
                        colors: [Color.blue.opacity(0.4), Color.indigo.opacity(0.2)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
        )
        .shadow(color: Color.black.opacity(0.45), radius: 20, y: 10)
    }

    private var header: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.blue, Color.indigo],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 42, height: 42)
                    .shadow(color: Color.blue.opacity(0.4), radius: 8, y: 4)

                Image(systemName: "train.side.front.car")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(data.trainName)
                    .font(.subheadline)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .lineLimit(1)

                HStack(spacing: 6) {
                    Text("#\(data.trainNumber)")
                        .font(.caption2)
                        .foregroundColor(Color.blue.opacity(0.9))

                    if let pnr = data.pnr {
                        Text("PNR: \(pnr)")
                            .font(.caption2)
                            .foregroundColor(Color.orange)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.orange.opacity(0.15))
                            .clipShape(Capsule())
                    }
                }
            }

            Spacer()

            if data.isLive {
                HStack(spacing: 4) {
                    Circle()
                        .fill(Color.green)
                        .frame(width: 6, height: 6)
                    Text("LIVE")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.green)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.green.opacity(0.15))
                .clipShape(Capsule())
            }
        }
        .padding(16)
        .background(
            LinearGradient(
                colors: [
                    Color.blue.opacity(0.2),
                    Color.indigo.opacity(0.08),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var journeySection: some View {
        VStack(spacing: 16) {
            HStack(alignment: .top) {
                // From Station
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 6) {
                        Circle()
                            .fill(Color.green)
                            .frame(width: 10, height: 10)
                        Text("FROM")
                            .font(.system(size: 9, weight: .bold))
                            .foregroundColor(Color.white.opacity(0.4))
                    }

                    Text(data.fromStation)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .lineLimit(2)

                    if let time = data.departureTime {
                        Text(time)
                            .font(.caption)
                            .fontWeight(.medium)
                            .foregroundColor(Color.green)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                // Journey Line
                VStack(spacing: 4) {
                    Image(systemName: "arrow.right")
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.3))

                    if let date = data.date {
                        Text(date)
                            .font(.caption2)
                            .foregroundColor(Color.white.opacity(0.5))
                    }
                }
                .padding(.top, 20)

                // To Station
                VStack(alignment: .trailing, spacing: 4) {
                    HStack(spacing: 6) {
                        Text("TO")
                            .font(.system(size: 9, weight: .bold))
                            .foregroundColor(Color.white.opacity(0.4))
                        Circle()
                            .fill(Color.red)
                            .frame(width: 10, height: 10)
                    }

                    Text(data.toStation)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .lineLimit(2)
                        .multilineTextAlignment(.trailing)

                    if let time = data.arrivalTime {
                        Text(time)
                            .font(.caption)
                            .fontWeight(.medium)
                            .foregroundColor(Color.orange)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .trailing)
            }

            // Delay indicator
            if let delay = data.delay, !delay.isEmpty {
                HStack(spacing: 6) {
                    Image(systemName: "clock.badge.exclamationmark")
                        .font(.caption)
                        .foregroundColor(.orange)
                    Text("Delayed by \(delay)")
                        .font(.caption)
                        .foregroundColor(.orange)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.orange.opacity(0.15))
                .clipShape(Capsule())
            }

            // Current Station
            if let current = data.currentStation {
                HStack(spacing: 8) {
                    Image(systemName: "location.fill")
                        .font(.caption)
                        .foregroundColor(Color.cyan)
                    Text("Currently at: \(current)")
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.8))
                    Spacer()
                }
            }
        }
        .padding(16)
    }

    private var passengersSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("PASSENGERS")
                .font(.caption2)
                .fontWeight(.bold)
                .foregroundColor(Color.white.opacity(0.4))
                .tracking(1)

            ForEach(Array(data.passengers.enumerated()), id: \.offset) { index, passenger in
                HStack {
                    Text("\(index + 1)")
                        .font(.caption2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .frame(width: 20, height: 20)
                        .background(Color.blue.opacity(0.3))
                        .clipShape(Circle())

                    if let name = passenger.name {
                        Text(name)
                            .font(.caption)
                            .foregroundColor(.white)
                            .lineLimit(1)
                    }

                    Spacer()

                    if let coach = passenger.coach {
                        Text(coach)
                            .font(.caption2)
                            .foregroundColor(Color.white.opacity(0.6))
                    }

                    Text(passenger.seat)
                        .font(.caption)
                        .foregroundColor(Color.cyan)

                    PassengerStatusBadge(status: passenger.status)
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 10)
                .background(Color.white.opacity(0.04))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }

    private var statusFooter: some View {
        HStack {
            Image(systemName: bookingStatusIcon)
                .font(.caption)
                .foregroundColor(bookingStatusColor)

            Text(data.status)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(bookingStatusColor)

            Spacer()

            if let updated = data.lastUpdated {
                Text("Updated: \(updated)")
                    .font(.caption2)
                    .foregroundColor(Color.white.opacity(0.4))
            }
        }
        .padding(12)
        .background(Color.black.opacity(0.3))
    }

    private var bookingStatusIcon: String {
        let status = data.status.lowercased()
        if status.contains("confirm") { return "checkmark.circle.fill" }
        if status.contains("waiting") || status.contains("wl") { return "clock.fill" }
        if status.contains("rac") { return "person.2.fill" }
        if status.contains("cancel") { return "xmark.circle.fill" }
        return "info.circle.fill"
    }

    private var bookingStatusColor: Color {
        let status = data.status.lowercased()
        if status.contains("confirm") { return .green }
        if status.contains("waiting") || status.contains("wl") { return .orange }
        if status.contains("rac") { return .yellow }
        if status.contains("cancel") { return .red }
        return .white
    }
}

private struct PassengerStatusBadge: View {
    let status: String

    var body: some View {
        Text(status)
            .font(.system(size: 10, weight: .bold))
            .foregroundColor(statusColor)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(statusColor.opacity(0.15))
            .clipShape(Capsule())
    }

    private var statusColor: Color {
        let s = status.lowercased()
        if s.contains("cnf") || s.contains("confirm") { return .green }
        if s.contains("wl") || s.contains("waiting") { return .orange }
        if s.contains("rac") { return .yellow }
        return .white
    }
}

// MARK: - Tarot Card

private struct TarotCardData: Equatable {
    let cardName: String
    let cardNumber: String?
    let meaning: String
    let interpretation: String?
    let advice: String?
    let isReversed: Bool
    let suit: String?
    let element: String?
    let keywords: [String]
}

private struct TarotCard: View {
    let data: TarotCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            cardImageSection
            meaningSection
            if let advice = data.advice, !advice.isEmpty {
                adviceSection(advice)
            }
            keywordsSection
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.12, green: 0.06, blue: 0.18),
                    Color(red: 0.06, green: 0.03, blue: 0.10)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(
                    LinearGradient(
                        colors: [Color.purple.opacity(0.5), Color.indigo.opacity(0.2)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
        )
        .shadow(color: Color.purple.opacity(0.3), radius: 20, y: 10)
    }

    private var header: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.purple, Color.indigo],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 42, height: 42)
                    .shadow(color: Color.purple.opacity(0.5), radius: 8, y: 4)

                Image(systemName: "suit.diamond.fill")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text("TAROT READING")
                    .font(.caption)
                    .fontWeight(.heavy)
                    .foregroundColor(Color.purple.opacity(0.9))
                    .tracking(1)

                if let suit = data.suit {
                    Text(suit)
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                }
            }

            Spacer()

            if data.isReversed {
                Text("REVERSED")
                    .font(.system(size: 9, weight: .bold))
                    .foregroundColor(.orange)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.15))
                    .clipShape(Capsule())
            }
        }
        .padding(16)
        .background(
            LinearGradient(
                colors: [
                    Color.purple.opacity(0.25),
                    Color.indigo.opacity(0.1),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var cardImageSection: some View {
        VStack(spacing: 12) {
            // Card representation
            ZStack {
                RoundedRectangle(cornerRadius: 12)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color.indigo.opacity(0.3),
                                Color.purple.opacity(0.2)
                            ],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .frame(width: 100, height: 150)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.white.opacity(0.2), lineWidth: 2)
                    )
                    .rotationEffect(.degrees(data.isReversed ? 180 : 0))

                VStack(spacing: 8) {
                    Text(cardEmoji)
                        .font(.system(size: 36))

                    if let number = data.cardNumber {
                        Text(number)
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(Color.white.opacity(0.7))
                    }
                }
                .rotationEffect(.degrees(data.isReversed ? 180 : 0))
            }
            .shadow(color: Color.purple.opacity(0.4), radius: 15, y: 8)

            VStack(spacing: 4) {
                Text(data.cardName)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

                if let element = data.element {
                    HStack(spacing: 6) {
                        Image(systemName: elementIcon)
                            .font(.caption)
                            .foregroundColor(elementColor)
                        Text(element)
                            .font(.caption2)
                            .foregroundColor(Color.white.opacity(0.6))
                    }
                }
            }
        }
        .padding(.vertical, 20)
        .frame(maxWidth: .infinity)
        .background(Color.black.opacity(0.2))
    }

    private var meaningSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 6) {
                Image(systemName: "sparkles")
                    .font(.caption)
                    .foregroundColor(Color.purple.opacity(0.8))
                Text("Meaning")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(Color.white.opacity(0.7))
            }

            Text(data.meaning)
                .font(.subheadline)
                .foregroundColor(Color.white.opacity(0.85))
                .lineSpacing(4)

            if let interpretation = data.interpretation, !interpretation.isEmpty {
                Text(interpretation)
                    .font(.caption)
                    .foregroundColor(Color.white.opacity(0.6))
                    .lineSpacing(3)
            }
        }
        .padding(16)
    }

    private func adviceSection(_ advice: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "lightbulb.fill")
                .font(.caption)
                .foregroundColor(Color.yellow.opacity(0.9))

            VStack(alignment: .leading, spacing: 4) {
                Text("Guidance")
                    .font(.caption2)
                    .fontWeight(.bold)
                    .foregroundColor(Color.white.opacity(0.5))
                Text(advice)
                    .font(.caption)
                    .foregroundColor(Color.white.opacity(0.8))
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.yellow.opacity(0.1))
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }

    private var keywordsSection: some View {
        Group {
            if !data.keywords.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(data.keywords, id: \.self) { keyword in
                            Text(keyword)
                                .font(.caption2)
                                .foregroundColor(Color.purple)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(Color.purple.opacity(0.15))
                                .clipShape(Capsule())
                        }
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.bottom, 14)
            }
        }
    }

    private var cardEmoji: String {
        let name = data.cardName.lowercased()
        if name.contains("fool") { return "🃏" }
        if name.contains("magician") { return "🎩" }
        if name.contains("priestess") { return "🌙" }
        if name.contains("empress") { return "👑" }
        if name.contains("emperor") { return "⚔️" }
        if name.contains("hierophant") { return "📿" }
        if name.contains("lovers") { return "💕" }
        if name.contains("chariot") { return "🏇" }
        if name.contains("strength") { return "🦁" }
        if name.contains("hermit") { return "🏔️" }
        if name.contains("wheel") { return "☸️" }
        if name.contains("justice") { return "⚖️" }
        if name.contains("hanged") { return "🙃" }
        if name.contains("death") { return "💀" }
        if name.contains("temperance") { return "⚗️" }
        if name.contains("devil") { return "😈" }
        if name.contains("tower") { return "🗼" }
        if name.contains("star") { return "⭐" }
        if name.contains("moon") { return "🌕" }
        if name.contains("sun") { return "☀️" }
        if name.contains("judgement") { return "📯" }
        if name.contains("world") { return "🌍" }
        if name.contains("wand") { return "🪄" }
        if name.contains("cup") { return "🏆" }
        if name.contains("sword") { return "⚔️" }
        if name.contains("pentacle") || name.contains("coin") { return "🪙" }
        return "🔮"
    }

    private var elementIcon: String {
        let element = (data.element ?? "").lowercased()
        if element.contains("fire") { return "flame.fill" }
        if element.contains("water") { return "drop.fill" }
        if element.contains("air") { return "wind" }
        if element.contains("earth") { return "leaf.fill" }
        return "sparkle"
    }

    private var elementColor: Color {
        let element = (data.element ?? "").lowercased()
        if element.contains("fire") { return .orange }
        if element.contains("water") { return .cyan }
        if element.contains("air") { return .white }
        if element.contains("earth") { return .green }
        return .purple
    }
}

// MARK: - Panchang Card

private struct PanchangCardData: Equatable {
    let date: String
    let day: String
    let tithi: String
    let nakshatra: String
    let yoga: String?
    let karana: String?
    let sunrise: String?
    let sunset: String?
    let moonrise: String?
    let moonset: String?
    let rahukaal: String?
    let auspiciousTime: String?
    let inauspiciousTime: String?
    let festival: String?
    let masa: String?
    let paksha: String?
}

private struct PanchangCard: View {
    let data: PanchangCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            mainInfoSection
            timingsSection
            if data.rahukaal != nil || data.auspiciousTime != nil {
                auspiciousSection
            }
            if let festival = data.festival, !festival.isEmpty {
                festivalSection(festival)
            }
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.12, green: 0.08, blue: 0.04),
                    Color(red: 0.06, green: 0.04, blue: 0.02)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(
                    LinearGradient(
                        colors: [Color.orange.opacity(0.5), Color.yellow.opacity(0.2)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
        )
        .shadow(color: Color.orange.opacity(0.2), radius: 20, y: 10)
    }

    private var header: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.orange, Color.yellow.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 42, height: 42)
                    .shadow(color: Color.orange.opacity(0.5), radius: 8, y: 4)

                Image(systemName: "calendar")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text("PANCHANG")
                    .font(.caption)
                    .fontWeight(.heavy)
                    .foregroundColor(Color.orange.opacity(0.9))
                    .tracking(1)

                Text(data.day)
                    .font(.caption2)
                    .foregroundColor(Color.white.opacity(0.6))
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 2) {
                Text(data.date)
                    .font(.subheadline)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

                if let masa = data.masa, let paksha = data.paksha {
                    Text("\(masa) • \(paksha)")
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                }
            }
        }
        .padding(16)
        .background(
            LinearGradient(
                colors: [
                    Color.orange.opacity(0.25),
                    Color.yellow.opacity(0.1),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var mainInfoSection: some View {
        VStack(spacing: 12) {
            HStack(spacing: 12) {
                PanchangInfoBox(
                    icon: "moon.stars.fill",
                    label: "Tithi",
                    value: data.tithi,
                    color: .yellow
                )

                PanchangInfoBox(
                    icon: "star.fill",
                    label: "Nakshatra",
                    value: data.nakshatra,
                    color: .cyan
                )
            }

            HStack(spacing: 12) {
                if let yoga = data.yoga {
                    PanchangInfoBox(
                        icon: "infinity",
                        label: "Yoga",
                        value: yoga,
                        color: .purple
                    )
                }

                if let karana = data.karana {
                    PanchangInfoBox(
                        icon: "circle.grid.2x2.fill",
                        label: "Karana",
                        value: karana,
                        color: .green
                    )
                }
            }
        }
        .padding(16)
    }

    private var timingsSection: some View {
        VStack(spacing: 10) {
            HStack {
                Text("TIMINGS")
                    .font(.caption2)
                    .fontWeight(.bold)
                    .foregroundColor(Color.white.opacity(0.4))
                    .tracking(1)
                Spacer()
            }

            HStack(spacing: 0) {
                if let sunrise = data.sunrise {
                    TimingPill(icon: "sunrise.fill", label: "Sunrise", time: sunrise, color: .orange)
                }

                if let sunset = data.sunset {
                    TimingPill(icon: "sunset.fill", label: "Sunset", time: sunset, color: .red)
                }

                if let moonrise = data.moonrise {
                    TimingPill(icon: "moon.fill", label: "Moonrise", time: moonrise, color: .white)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }

    private var auspiciousSection: some View {
        VStack(spacing: 8) {
            if let rahukaal = data.rahukaal {
                HStack(spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundColor(.red)
                    Text("Rahu Kaal:")
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.6))
                    Text(rahukaal)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.red)
                    Spacer()
                }
                .padding(10)
                .background(Color.red.opacity(0.1))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            }

            if let auspicious = data.auspiciousTime {
                HStack(spacing: 8) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.caption)
                        .foregroundColor(.green)
                    Text("Shubh Muhurat:")
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.6))
                    Text(auspicious)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.green)
                    Spacer()
                }
                .padding(10)
                .background(Color.green.opacity(0.1))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }

    private func festivalSection(_ festival: String) -> some View {
        HStack(spacing: 10) {
            Text("🪔")
                .font(.title3)

            VStack(alignment: .leading, spacing: 2) {
                Text("Festival")
                    .font(.caption2)
                    .foregroundColor(Color.white.opacity(0.5))
                Text(festival)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(Color.yellow)
            }

            Spacer()
        }
        .padding(12)
        .background(
            LinearGradient(
                colors: [Color.orange.opacity(0.2), Color.yellow.opacity(0.1)],
                startPoint: .leading,
                endPoint: .trailing
            )
        )
    }
}

private struct PanchangInfoBox: View {
    let icon: String
    let label: String
    let value: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.caption)
                    .foregroundColor(color)
                Text(label)
                    .font(.caption2)
                    .foregroundColor(Color.white.opacity(0.5))
            }

            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.white)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }
}

private struct TimingPill: View {
    let icon: String
    let label: String
    let time: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundColor(color)
            Text(time)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.white)
            Text(label)
                .font(.system(size: 8))
                .foregroundColor(Color.white.opacity(0.4))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
    }
}

private struct HoroscopeCardData: Equatable {
    let sign: String
    let period: String
    let horoscope: String
    let luckyNumber: String?
    let luckyColor: String?
    let mood: String?
    let compatibility: String?
    let focusArea: String?
    let advice: String?
}

private struct HoroscopeCard: View {
    let data: HoroscopeCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            content
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.1, green: 0.08, blue: 0.16),
                    Color.black
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.white.opacity(0.06), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.35), radius: 18, y: 10)
    }

    private var header: some View {
        HStack(spacing: 12) {
            Text(zodiacEmoji)
                .font(.system(size: 34))
            VStack(alignment: .leading, spacing: 2) {
                Text(data.sign.capitalized)
                    .font(.headline)
                    .foregroundColor(.white)
                Text(data.period.capitalized)
                    .font(.caption)
                    .foregroundColor(Color.white.opacity(0.6))
            }
            Spacer()
            Image(systemName: "sparkles")
                .foregroundColor(Color.yellow.opacity(0.9))
        }
        .padding(14)
        .background(
            LinearGradient(
                colors: headerGradientColors,
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var content: some View {
        VStack(alignment: .leading, spacing: 12) {
            if !data.horoscope.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    HStack(spacing: 6) {
                        Image(systemName: "star.fill")
                            .font(.caption)
                            .foregroundColor(Color.yellow.opacity(0.9))
                        Text("Today's Reading")
                            .font(.caption)
                            .foregroundColor(Color.white.opacity(0.7))
                    }
                    Text(data.horoscope)
                        .font(.subheadline)
                        .foregroundColor(Color.white.opacity(0.75))
                }
                .padding(12)
                .background(Color.white.opacity(0.06))
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }

            if data.luckyNumber != nil || data.luckyColor != nil {
                HStack(spacing: 10) {
                    if let number = data.luckyNumber {
                        VStack(spacing: 4) {
                            Text("Lucky Number")
                                .font(.caption2)
                                .foregroundColor(Color.white.opacity(0.5))
                            Text(number)
                                .font(.title3)
                                .foregroundColor(Color.purple.opacity(0.9))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(10)
                        .background(Color.white.opacity(0.05))
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                    }

                    if let color = data.luckyColor {
                        VStack(spacing: 4) {
                            Text("Lucky Color")
                                .font(.caption2)
                                .foregroundColor(Color.white.opacity(0.5))
                            Text(color.capitalized)
                                .font(.caption)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(Color.white.opacity(0.08))
                                .clipShape(Capsule())
                                .foregroundColor(.white)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(10)
                        .background(Color.white.opacity(0.05))
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                    }
                }
            }

            if data.mood != nil || data.compatibility != nil || data.focusArea != nil {
                VStack(alignment: .leading, spacing: 6) {
                    if let mood = data.mood {
                        HoroscopeMetaRow(icon: "moon.stars.fill", label: "Mood", value: mood)
                    }
                    if let focus = data.focusArea {
                        HoroscopeMetaRow(icon: "star.circle.fill", label: "Focus", value: focus)
                    }
                    if let match = data.compatibility {
                        HoroscopeMetaRow(icon: "sun.max.fill", label: "Best match", value: match)
                    }
                }
                .padding(.top, 6)
            }

            if let advice = data.advice, !advice.isEmpty {
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "sparkles")
                        .font(.caption)
                        .foregroundColor(Color.purple.opacity(0.8))
                    Text(advice)
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.75))
                }
                .padding(10)
                .background(Color.purple.opacity(0.12))
                .clipShape(RoundedRectangle(cornerRadius: 10))
            }
        }
        .padding(14)
    }

    private var zodiacEmoji: String {
        let key = data.sign.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return HoroscopeCard.zodiacEmojis[key] ?? "⭐"
    }

    private var headerGradientColors: [Color] {
        let key = data.sign.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return HoroscopeCard.zodiacGradients[key] ?? [
            Color.purple.opacity(0.35),
            Color.purple.opacity(0.15)
        ]
    }

    private static let zodiacEmojis: [String: String] = [
        "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋",
        "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
        "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓"
    ]

    private static let zodiacGradients: [String: [Color]] = [
        "aries": [Color.red.opacity(0.35), Color.orange.opacity(0.2)],
        "taurus": [Color.green.opacity(0.35), Color.mint.opacity(0.2)],
        "gemini": [Color.yellow.opacity(0.35), Color.orange.opacity(0.2)],
        "cancer": [Color.blue.opacity(0.35), Color.cyan.opacity(0.2)],
        "leo": [Color.orange.opacity(0.35), Color.yellow.opacity(0.2)],
        "virgo": [Color.green.opacity(0.35), Color.teal.opacity(0.2)],
        "libra": [Color.pink.opacity(0.35), Color.purple.opacity(0.2)],
        "scorpio": [Color.purple.opacity(0.35), Color.indigo.opacity(0.2)],
        "sagittarius": [Color.indigo.opacity(0.35), Color.blue.opacity(0.2)],
        "capricorn": [Color.gray.opacity(0.35), Color.black.opacity(0.2)],
        "aquarius": [Color.cyan.opacity(0.35), Color.blue.opacity(0.2)],
        "pisces": [Color.purple.opacity(0.35), Color.pink.opacity(0.2)]
    ]
}

private struct HoroscopeMetaRow: View {
    let icon: String
    let label: String
    let value: String

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundColor(Color.white.opacity(0.5))
            Text("\(label):")
                .font(.caption)
                .foregroundColor(Color.white.opacity(0.5))
            Text(value.capitalized)
                .font(.caption)
                .foregroundColor(Color.white.opacity(0.8))
        }
    }
}

private struct NewsCardData: Equatable {
    let items: [NewsItem]
    let category: String?
}

private struct NewsItem: Equatable {
    let title: String
    let summary: String?
    let source: String?
    let url: String?
    let publishedAt: String?
    let imageURL: String?
    let category: String?
}

private struct NewsCard: View {
    let items: [NewsItem]
    let category: String?

    var body: some View {
        VStack(spacing: 0) {
            header
            VStack(spacing: 10) {
                ForEach(items.prefix(5), id: \.title) { item in
                    NewsItemRow(item: item)
                }
            }
            .padding(14)
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.08, green: 0.07, blue: 0.12),
                    Color.black
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.white.opacity(0.06), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.35), radius: 18, y: 10)
    }

    private var header: some View {
        HStack(spacing: 10) {
            Image(systemName: "newspaper.fill")
                .foregroundColor(Color.cyan.opacity(0.85))
            Text(categoryTitle)
                .font(.headline)
                .foregroundColor(.white)
            Spacer()
            Text("\(items.count) articles")
                .font(.caption2)
                .foregroundColor(Color.white.opacity(0.6))
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.08))
                .clipShape(Capsule())
        }
        .padding(14)
        .background(
            LinearGradient(
                colors: [
                    Color.cyan.opacity(0.2),
                    Color.blue.opacity(0.08)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var categoryTitle: String {
        if let category, !category.isEmpty {
            return "\(category.capitalized) News"
        }
        return "Latest News"
    }
}

private struct NewsItemRow: View {
    let item: NewsItem

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .top, spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    if let url = item.url, let link = URL(string: url) {
                        Link(destination: link) {
                            Text(item.title)
                                .font(.subheadline)
                                .foregroundColor(.white)
                                .multilineTextAlignment(.leading)
                        }
                    } else {
                        Text(item.title)
                            .font(.subheadline)
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                    }

                    if let summary = item.summary, !summary.isEmpty {
                        Text(summary)
                            .font(.caption)
                            .foregroundColor(Color.white.opacity(0.6))
                            .lineLimit(2)
                    }
                }

                if let imageURL = item.imageURL, let url = URL(string: imageURL) {
                    AsyncImage(url: url) { phase in
                        switch phase {
                        case .empty:
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.white.opacity(0.08))
                        case .success(let image):
                            image
                                .resizable()
                                .scaledToFill()
                        default:
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.white.opacity(0.08))
                        }
                    }
                    .frame(width: 60, height: 60)
                    .clipped()
                    .cornerRadius(8)
                }
            }

            HStack(spacing: 10) {
                if let source = item.source, !source.isEmpty {
                    Label(source, systemImage: "tag")
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                }
                if let publishedAt = item.publishedAt, !publishedAt.isEmpty {
                    Label(publishedAt, systemImage: "clock")
                        .font(.caption2)
                        .foregroundColor(Color.white.opacity(0.5))
                }
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.04))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

private struct NumerologyCardData: Equatable {
    let name: String
    let nameNumber: String?
    let nameTrait: String?
    let nameDescription: String?
    let lifePathNumber: String?
    let lifePathTrait: String?
    let expressionNumber: String?
    let soulUrgeNumber: String?
    let personalityNumber: String?
    let luckyNumbers: [String]
}

private struct NumerologyCard: View {
    let data: NumerologyCardData

    var body: some View {
        ZStack(alignment: .topTrailing) {
            RoundedRectangle(cornerRadius: 20)
                .fill(
                    LinearGradient(
                        colors: [
                            Color(red: 0.07, green: 0.05, blue: 0.15),
                            Color(red: 0.12, green: 0.07, blue: 0.2)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )

            Circle()
                .fill(Color.pink.opacity(0.15))
                .frame(width: 120, height: 120)
                .offset(x: 40, y: -40)

            VStack(alignment: .leading, spacing: 14) {
                header
                heroRow
                if let description = data.nameDescription, !description.isEmpty {
                    descriptionBlock(text: description)
                }
                detailChips
                if !data.luckyNumbers.isEmpty {
                    luckyRow
                }
            }
            .padding(16)
        }
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.35), radius: 18, y: 10)
    }

    private var header: some View {
        HStack(spacing: 10) {
            Image(systemName: "circle.grid.2x2.fill")
                .foregroundColor(Color.pink.opacity(0.9))
            VStack(alignment: .leading, spacing: 2) {
                Text(data.name)
                    .font(.headline)
                    .foregroundColor(.white)
                Text(data.nameTrait?.capitalized ?? "Numerology Insight")
                    .font(.caption)
                    .foregroundColor(Color.white.opacity(0.6))
            }
            Spacer()
            Text("#\(data.lifePathNumber ?? "—")")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(Color.white.opacity(0.7))
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.08))
                .clipShape(Capsule())
        }
    }

    private var heroRow: some View {
        HStack(alignment: .top, spacing: 14) {
            NumerologyHeroNumber(
                title: "Life Path",
                value: data.lifePathNumber ?? "—",
                accent: Color.purple
            )

            VStack(alignment: .leading, spacing: 8) {
                NumerologyHeroNumber(
                    title: "Name Number",
                    value: data.nameNumber ?? "—",
                    accent: Color.orange
                )

                if let trait = data.lifePathTrait, !trait.isEmpty {
                    Text(trait.capitalized)
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.7))
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var detailChips: some View {
        VStack(spacing: 8) {
            HStack(spacing: 8) {
                NumerologyChip(label: "Expression", value: data.expressionNumber)
                NumerologyChip(label: "Soul Urge", value: data.soulUrgeNumber)
            }
            HStack(spacing: 8) {
                NumerologyChip(label: "Personality", value: data.personalityNumber)
                NumerologyChip(label: "Trait", value: data.lifePathTrait)
            }
        }
    }

    private var luckyRow: some View {
        HStack(spacing: 10) {
            Image(systemName: "sparkle")
                .font(.caption)
                .foregroundColor(Color.pink.opacity(0.85))
            Text("Lucky")
                .font(.caption)
                .foregroundColor(Color.white.opacity(0.6))
            Text(data.luckyNumbers.joined(separator: " • "))
                .font(.caption)
                .foregroundColor(.white)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.06))
        .clipShape(Capsule())
    }

    private func descriptionBlock(text: String) -> some View {
        Text(text)
            .font(.caption)
            .foregroundColor(Color.white.opacity(0.75))
            .padding(10)
            .background(Color.white.opacity(0.06))
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

private struct NumerologyHeroNumber: View {
    let title: String
    let value: String
    let accent: Color

    var body: some View {
        VStack(spacing: 6) {
            Text(title)
                .font(.caption2)
                .foregroundColor(Color.white.opacity(0.6))
            Text(value)
                .font(.title)
                .fontWeight(.semibold)
                .foregroundColor(.white)
                .frame(width: 64, height: 64)
                .background(
                    LinearGradient(
                        colors: [
                            accent.opacity(0.7),
                            accent.opacity(0.3)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .clipShape(Circle())
        }
        .padding(10)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}

private struct NumerologyChip: View {
    let label: String
    let value: String?

    var body: some View {
        HStack(spacing: 6) {
            Text(label)
                .font(.caption2)
                .foregroundColor(Color.white.opacity(0.6))
            Spacer()
            Text(value ?? "—")
                .font(.caption)
                .foregroundColor(.white)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }
}

// MARK: - Places Card

private struct PlacesCardData: Equatable {
    let title: String
    let query: String?
    let location: String?
    let items: [PlaceItem]
}

private struct PlaceItem: Equatable {
    let name: String
    let address: String?
    let rating: Double?
    let reviewCount: Int?
    let price: String?
    let distance: String?
    let isOpen: Bool?
    let url: String?
    let imageURL: String?
}

private struct PlacesCard: View {
    let data: PlacesCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            VStack(spacing: 12) {
                ForEach(Array(data.items.prefix(6).enumerated()), id: \.offset) { index, item in
                    PlaceRow(item: item, index: index + 1)
                }
            }
            .padding(16)
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.06, green: 0.05, blue: 0.1),
                    Color(red: 0.03, green: 0.03, blue: 0.07)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(Color.orange.opacity(0.25), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.35), radius: 18, y: 8)
    }

    private var header: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.orange, Color.pink],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 40, height: 40)

                Image(systemName: "fork.knife")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 3) {
                Text(data.title.uppercased())
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .tracking(1)

                if let query = data.query, !query.isEmpty {
                    Text(query)
                        .font(.caption)
                        .foregroundColor(Color.orange.opacity(0.85))
                        .lineLimit(1)
                } else if let location = data.location, !location.isEmpty {
                    Text(location)
                        .font(.caption)
                        .foregroundColor(Color.orange.opacity(0.85))
                        .lineLimit(1)
                }
            }

            Spacer()

            Text("\(data.items.count) places")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.6))
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.08))
                .clipShape(Capsule())
        }
        .padding(16)
        .background(
            LinearGradient(
                colors: [
                    Color.orange.opacity(0.2),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }
}

private struct PlaceRow: View {
    let item: PlaceItem
    let index: Int

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(index)")
                .font(.caption2)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .frame(width: 22, height: 22)
                .background(Color.orange.opacity(0.7))
                .clipShape(Circle())

            VStack(alignment: .leading, spacing: 6) {
                if let url = item.url, let link = URL(string: url) {
                    Link(destination: link) {
                        Text(item.name)
                            .font(.subheadline)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                    }
                } else {
                    Text(item.name)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .multilineTextAlignment(.leading)
                }

                if let address = item.address, !address.isEmpty {
                    Text(address)
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.6))
                        .lineLimit(2)
                }

                HStack(spacing: 8) {
                    if let rating = item.rating {
                        RatingBadge(rating: rating, reviewCount: item.reviewCount)
                    }
                    if let distance = item.distance, !distance.isEmpty {
                        MiniChip(icon: "location.fill", text: distance, color: .blue)
                    }
                    if let price = item.price, !price.isEmpty {
                        MiniChip(icon: "tag.fill", text: price, color: .orange)
                    }
                    if let isOpen = item.isOpen {
                        MiniChip(icon: "clock.fill", text: isOpen ? "Open" : "Closed", color: isOpen ? .green : .red)
                    }
                }
            }

            Spacer()
        }
        .padding(12)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}

private struct RatingBadge: View {
    let rating: Double
    let reviewCount: Int?

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: "star.fill")
                .font(.system(size: 10, weight: .bold))
                .foregroundColor(.yellow)
            Text(String(format: "%.1f", rating))
                .font(.caption2)
                .fontWeight(.bold)
                .foregroundColor(.white)
            if let reviewCount {
                Text("(\(reviewCount))")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.6))
            }
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color.white.opacity(0.08))
        .clipShape(Capsule())
    }
}

// MARK: - Government Jobs Card

private struct GovtJobsCardData: Equatable {
    let items: [GovtJobItem]
    let searchQuery: String?
    let totalJobs: Int
    let totalVacancies: Int?
    let date: String?
}

private struct GovtJobItem: Equatable {
    let title: String
    let organization: String?
    let vacancies: String?
    let lastDate: String?
    let qualification: String?
    let salary: String?
    let location: String?
    let url: String?
    let isNew: Bool
    let snippet: String?
}

private struct GovtJobsCard: View {
    let data: GovtJobsCardData

    var body: some View {
        VStack(spacing: 0) {
            header
            statsRow
            ScrollView {
                VStack(spacing: 14) {
                    ForEach(Array(data.items.prefix(5).enumerated()), id: \.element.title) { index, item in
                        GovtJobItemRow(item: item, index: index + 1)
                    }
                }
                .padding(16)
            }
            .frame(maxHeight: 450)
            footer
        }
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.04, green: 0.06, blue: 0.12),
                    Color(red: 0.02, green: 0.03, blue: 0.06)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 22))
        .overlay(
            RoundedRectangle(cornerRadius: 22)
                .stroke(
                    LinearGradient(
                        colors: [Color.blue.opacity(0.3), Color.indigo.opacity(0.1)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
        )
        .shadow(color: Color.black.opacity(0.5), radius: 25, y: 12)
    }

    private var header: some View {
        HStack(spacing: 14) {
            // Animated Icon
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.orange, Color.red.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 48, height: 48)
                    .shadow(color: Color.orange.opacity(0.4), radius: 8, y: 4)

                Image(systemName: "building.columns.fill")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 6) {
                    Text("🇮🇳")
                        .font(.caption)
                    Text("SARKARI NAUKRI")
                        .font(.subheadline)
                        .fontWeight(.heavy)
                        .foregroundColor(.white)
                        .tracking(1)
                }

                Text(cleanSearchQuery(data.searchQuery))
                    .font(.caption)
                    .foregroundColor(Color.orange.opacity(0.9))
                    .fontWeight(.medium)
                    .lineLimit(1)
            }

            Spacer()

            // Live Badge
            HStack(spacing: 4) {
                Circle()
                    .fill(Color.green)
                    .frame(width: 6, height: 6)
                Text("LIVE")
                    .font(.system(size: 9, weight: .bold))
                    .foregroundColor(.green)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.green.opacity(0.15))
            .clipShape(Capsule())
        }
        .padding(18)
        .background(
            LinearGradient(
                colors: [
                    Color.orange.opacity(0.2),
                    Color.red.opacity(0.1),
                    Color.clear
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var statsRow: some View {
        HStack(spacing: 0) {
            // Total Jobs
            StatBox(
                icon: "briefcase.fill",
                value: "\(data.totalJobs)",
                label: "Jobs Found",
                color: .blue
            )

            Divider()
                .frame(height: 40)
                .background(Color.white.opacity(0.1))

            // Total Vacancies
            StatBox(
                icon: "person.3.fill",
                value: data.totalVacancies != nil ? "\(data.totalVacancies!)" : "1000+",
                label: "Total Posts",
                color: .orange
            )

            Divider()
                .frame(height: 40)
                .background(Color.white.opacity(0.1))

            // Date
            StatBox(
                icon: "calendar",
                value: data.date ?? "Today",
                label: "Updated",
                color: .green
            )
        }
        .padding(.vertical, 12)
        .background(Color.white.opacity(0.03))
    }

    private var footer: some View {
        HStack {
            Image(systemName: "info.circle.fill")
                .font(.caption)
                .foregroundColor(Color.white.opacity(0.4))
            Text("Tap on job for details • Swipe for more")
                .font(.caption2)
                .foregroundColor(Color.white.opacity(0.4))
            Spacer()
            Text("sarkariresult.com")
                .font(.caption2)
                .foregroundColor(Color.blue.opacity(0.6))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Color.black.opacity(0.3))
    }
}

private struct StatBox: View {
    let icon: String
    let value: String
    let label: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 12))
                    .foregroundColor(color)
                Text(value)
                    .font(.subheadline)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
            }
            Text(label)
                .font(.system(size: 9))
                .foregroundColor(Color.white.opacity(0.5))
        }
        .frame(maxWidth: .infinity)
    }
}

private struct GovtJobItemRow: View {
    let item: GovtJobItem
    let index: Int

    // Extract organization from title if not provided
    private var displayOrganization: String {
        if let org = item.organization, !org.isEmpty {
            return org
        }
        // Try to extract from title
        let title = item.title.lowercased()
        let orgs: [(String, String)] = [
            ("bpsc", "BPSC"), ("upsc", "UPSC"), ("ssc", "SSC"),
            ("railway", "Railways"), ("rrb", "RRB"), ("ibps", "IBPS"),
            ("sbi", "SBI"), ("rbi", "RBI"), ("aiims", "AIIMS"),
            ("drdo", "DRDO"), ("isro", "ISRO"), ("army", "Army"),
            ("navy", "Navy"), ("police", "Police"), ("bank", "Bank")
        ]
        for (key, name) in orgs {
            if title.contains(key) {
                return name
            }
        }
        return ""
    }

    // Extract posts/vacancies from title or snippet
    private var displayVacancies: String {
        if let vac = item.vacancies, !vac.isEmpty {
            return vac
        }
        // Try to extract from title/snippet
        let text = "\(item.title) \(item.snippet ?? "")"
        if let match = text.range(of: #"(\d+(?:,\d+)*)\s*(?:posts?|vacancies|पद)"#, options: .regularExpression, range: nil, locale: nil) {
            let extracted = String(text[match])
            if let numMatch = extracted.range(of: #"\d+(?:,\d+)*"#, options: .regularExpression) {
                return String(extracted[numMatch])
            }
        }
        return ""
    }

    // Extract last date from title or snippet
    private var displayLastDate: String {
        if let date = item.lastDate, !date.isEmpty {
            return date
        }
        // Try to extract from snippet
        let text = item.snippet ?? ""
        if let match = text.range(of: #"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"#, options: .regularExpression) {
            return String(text[match])
        }
        return ""
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header Row: Index, Title, NEW Badge
            HStack(alignment: .top, spacing: 10) {
                // Index Number
                Text("\(index)")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .frame(width: 24, height: 24)
                    .background(
                        LinearGradient(
                            colors: [Color.orange, Color.red.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .clipShape(Circle())

                VStack(alignment: .leading, spacing: 6) {
                    // Title
                    if let url = item.url, let link = URL(string: url) {
                        Link(destination: link) {
                            Text(cleanJobTitle(item.title))
                                .font(.subheadline)
                                .fontWeight(.semibold)
                                .foregroundColor(.white)
                                .multilineTextAlignment(.leading)
                                .lineLimit(2)
                        }
                    } else {
                        Text(cleanJobTitle(item.title))
                            .font(.subheadline)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                            .lineLimit(2)
                    }

                    // Organization Badge
                    if !displayOrganization.isEmpty {
                        HStack(spacing: 5) {
                            Image(systemName: "building.columns.fill")
                                .font(.system(size: 10))
                                .foregroundColor(Color.blue)
                            Text(displayOrganization)
                                .font(.caption2)
                                .fontWeight(.semibold)
                                .foregroundColor(Color.blue)
                        }
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.15))
                        .clipShape(Capsule())
                    }
                }

                Spacer()

                // NEW Badge
                if item.isNew {
                    Text("NEW")
                        .font(.system(size: 8, weight: .heavy))
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            LinearGradient(
                                colors: [Color.green, Color.mint],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .clipShape(Capsule())
                        .shadow(color: Color.green.opacity(0.4), radius: 4, y: 2)
                }
            }

            // Key Details - Always show row with available info
            let hasVacancies = !displayVacancies.isEmpty
            let hasLastDate = !displayLastDate.isEmpty
            let hasSalary = item.salary != nil && !item.salary!.isEmpty
            let hasQualification = item.qualification != nil && !item.qualification!.isEmpty
            let hasLocation = item.location != nil && !item.location!.isEmpty

            if hasVacancies || hasLastDate || hasSalary {
                HStack(spacing: 8) {
                    if hasVacancies {
                        KeyInfoPill(icon: "person.3.fill", text: "\(displayVacancies) Posts", color: .orange)
                    }

                    if hasLastDate {
                        KeyInfoPill(icon: "calendar.badge.exclamationmark", text: displayLastDate, color: .red)
                    }

                    if hasSalary {
                        KeyInfoPill(icon: "indianrupeesign.circle.fill", text: item.salary!, color: .green)
                    }
                }
            }

            // Secondary Details Row
            if hasQualification || hasLocation {
                HStack(spacing: 8) {
                    if hasQualification {
                        MiniChip(icon: "graduationcap.fill", text: item.qualification!, color: .purple)
                    }

                    if hasLocation {
                        MiniChip(icon: "mappin.circle.fill", text: item.location!, color: .cyan)
                    }
                }
            }

            // Snippet if available and meaningful
            if let snippet = item.snippet, !snippet.isEmpty, snippet.count > 20 {
                Text(snippet)
                    .font(.caption2)
                    .foregroundColor(Color.white.opacity(0.55))
                    .lineLimit(2)
                    .padding(.top, 2)
            }

            // Apply Button Row
            if let url = item.url, let link = URL(string: url) {
                HStack {
                    Spacer()
                    Link(destination: link) {
                        HStack(spacing: 6) {
                            Image(systemName: "doc.text.fill")
                                .font(.system(size: 10))
                            Text("View & Apply")
                                .font(.caption)
                                .fontWeight(.semibold)
                            Image(systemName: "arrow.right")
                                .font(.system(size: 9, weight: .bold))
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 9)
                        .background(
                            LinearGradient(
                                colors: [Color.blue, Color.indigo],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .clipShape(Capsule())
                        .shadow(color: Color.blue.opacity(0.3), radius: 5, y: 2)
                    }
                }
            }
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.white.opacity(0.07),
                            Color.white.opacity(0.03)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }

    private func cleanJobTitle(_ title: String) -> String {
        var cleaned = title
            .replacingOccurrences(of: " - FreeJobAlert.Com", with: "")
            .replacingOccurrences(of: " - Sarkari Result", with: "")
            .replacingOccurrences(of: " | FreeJobAlert", with: "")
            .replacingOccurrences(of: " - SarkariResult", with: "")
            .replacingOccurrences(of: "Recruitment", with: "")
            .replacingOccurrences(of: "Advertisement", with: "")
            .trimmingCharacters(in: CharacterSet(charactersIn: " -|"))

        // Limit length
        if cleaned.count > 60 {
            cleaned = String(cleaned.prefix(57)) + "..."
        }

        return cleaned.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

private struct KeyInfoPill: View {
    let icon: String
    let text: String
    let color: Color

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 10, weight: .semibold))
            Text(text)
                .font(.caption2)
                .fontWeight(.semibold)
        }
        .foregroundColor(color)
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(color.opacity(0.15))
        .clipShape(Capsule())
    }
}

private struct MiniChip: View {
    let icon: String
    let text: String
    let color: Color

    var body: some View {
        HStack(spacing: 3) {
            Image(systemName: icon)
                .font(.system(size: 8))
            Text(text)
                .font(.system(size: 10))
        }
        .foregroundColor(color.opacity(0.8))
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color.white.opacity(0.05))
        .clipShape(Capsule())
    }
}

/// Clean up search query for display
private func cleanSearchQuery(_ query: String?) -> String {
    guard let query = query, !query.isEmpty else {
        return "Latest Government Jobs"
    }

    // Remove site: filters and OR operators
    var cleaned = query
        .replacingOccurrences(of: "site:gov.in", with: "")
        .replacingOccurrences(of: "site:nic.in", with: "")
        .replacingOccurrences(of: "site:india.gov.in", with: "")
        .replacingOccurrences(of: "site:.gov.in", with: "")
        .replacingOccurrences(of: "site:freejobalert.com", with: "")
        .replacingOccurrences(of: "site:sarkariresult.com", with: "")
        .replacingOccurrences(of: "site:employmentnews.gov.in", with: "")
        .replacingOccurrences(of: "site:ssc.nic.in", with: "")
        .replacingOccurrences(of: "site:upsc.gov.in", with: "")
        .replacingOccurrences(of: " OR ", with: " ")
        .replacingOccurrences(of: "government jobs", with: "")
        .replacingOccurrences(of: "latest vacancy", with: "")
        .replacingOccurrences(of: "notification", with: "")
        .replacingOccurrences(of: "recruitment", with: "")
        .replacingOccurrences(of: "2026", with: "")
        .replacingOccurrences(of: "2025", with: "")

    // Clean up multiple spaces
    while cleaned.contains("  ") {
        cleaned = cleaned.replacingOccurrences(of: "  ", with: " ")
    }

    cleaned = cleaned.trimmingCharacters(in: .whitespacesAndNewlines)

    // If we have a state/region name, format nicely
    if !cleaned.isEmpty {
        return "\(cleaned.capitalized) Jobs"
    }

    return "Latest Government Jobs"
}

private struct WeatherCard: View {
    let data: WeatherCardData

    var body: some View {
        VStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 14) {
                HStack(spacing: 8) {
                    Image(systemName: "location.fill")
                        .font(.caption)
                        .foregroundColor(Color.white.opacity(0.55))
                    Text(data.city)
                        .font(.subheadline)
                        .foregroundColor(Color.white.opacity(0.65))
                }

                HStack(alignment: .center, spacing: 16) {
                    VStack(alignment: .leading, spacing: 6) {
                        HStack(alignment: .firstTextBaseline, spacing: 6) {
                            Text("\(Int(round(data.temperature)))")
                                .font(.system(size: 44, weight: .bold))
                                .foregroundColor(.white)
                            Text("°C")
                                .font(.headline)
                                .foregroundColor(Color.white.opacity(0.7))
                        }
                        Text(data.condition.capitalized)
                            .font(.headline)
                            .foregroundColor(Color.white.opacity(0.8))
                        Text("Feels like \(Int(round(data.temperature)))°C")
                            .font(.footnote)
                            .foregroundColor(Color.white.opacity(0.5))
                    }

                    Spacer()

                    Image(systemName: "cloud.fill")
                        .font(.system(size: 46))
                        .foregroundColor(Color.white.opacity(0.6))
                }
            }
            .padding(16)
            .background(
                LinearGradient(
                    colors: [
                        Color(red: 0.17, green: 0.1, blue: 0.24),
                        Color(red: 0.08, green: 0.06, blue: 0.11)
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )

            Divider()
                .background(Color.white.opacity(0.06))

            HStack {
                WeatherStat(
                    icon: "drop.fill",
                    iconColor: .cyan,
                    label: "Humidity",
                    value: "\(Int(round(data.humidity)))%"
                )

                Divider()
                    .background(Color.white.opacity(0.08))

                WeatherStat(
                    icon: "wind",
                    iconColor: .white.opacity(0.7),
                    label: "Wind",
                    value: windValue
                )

                Divider()
                    .background(Color.white.opacity(0.08))

                WeatherStat(
                    icon: "eye.fill",
                    iconColor: .orange,
                    label: "Visibility",
                    value: visibilityValue
                )
            }
            .padding(.vertical, 12)
            .background(Color(red: 0.07, green: 0.06, blue: 0.1))
        }
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.white.opacity(0.06), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.35), radius: 18, y: 10)
    }

    private var windValue: String {
        guard let speed = data.windSpeed else { return "—" }
        return String(format: "%.1f m/s", speed)
    }

    private var visibilityValue: String {
        guard let km = data.visibilityKm else { return "—" }
        return String(format: "%.1f km", km)
    }
}

private struct WeatherStat: View {
    let icon: String
    let iconColor: Color
    let label: String
    let value: String

    var body: some View {
        VStack(spacing: 6) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundColor(iconColor)
            Text(label)
                .font(.caption2)
                .foregroundColor(Color.white.opacity(0.55))
            Text(value)
                .font(.subheadline)
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Email List Card

private struct EmailListItem: Equatable {
    let id: String
    let subject: String
    let from: String
    let date: String
    let snippet: String
}

private struct EmailListCardData: Equatable {
    let emails: [EmailListItem]
    let count: Int
}

private struct EmailListChatCard: View {
    let data: EmailListCardData

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack(spacing: 8) {
                Image(systemName: "envelope.fill")
                    .font(.system(size: 16))
                    .foregroundColor(.blue)
                Text("Emails (\(data.count))")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                Spacer()
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(
                LinearGradient(
                    colors: [Color.blue.opacity(0.25), Color.purple.opacity(0.15)],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )

            // Email rows
            ForEach(Array(data.emails.enumerated()), id: \.element.id) { index, email in
                if index > 0 {
                    Divider()
                        .background(Color.white.opacity(0.1))
                }

                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(parseSenderName(email.from))
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .lineLimit(1)

                        Spacer()

                        Text(smartDate(email.date))
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.5))
                    }

                    Text(email.subject.isEmpty ? "(No subject)" : email.subject)
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.white.opacity(0.9))
                        .lineLimit(1)

                    Text(email.snippet)
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.5))
                        .lineLimit(1)
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(red: 0.14, green: 0.11, blue: 0.19))
        )
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.blue.opacity(0.2), lineWidth: 1)
        )
    }

    private func parseSenderName(_ from: String) -> String {
        if let angle = from.firstIndex(of: "<") {
            return String(from[from.startIndex..<angle]).trimmingCharacters(in: .whitespaces)
        }
        if from.contains("@") {
            return String(from.split(separator: "@").first ?? Substring(from))
        }
        return from
    }

    private func smartDate(_ dateStr: String) -> String {
        let formatter = DateFormatter()
        let formats = [
            "EEE, dd MMM yyyy HH:mm:ss Z",
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
            "dd MMM yyyy HH:mm:ss Z"
        ]
        var parsed: Date?
        for format in formats {
            formatter.dateFormat = format
            formatter.locale = Locale(identifier: "en_US_POSIX")
            if let date = formatter.date(from: dateStr) {
                parsed = date
                break
            }
        }
        guard let date = parsed else { return String(dateStr.prefix(10)) }
        let calendar = Calendar.current
        if calendar.isDateInToday(date) {
            let tf = DateFormatter()
            tf.dateFormat = "h:mm a"
            return tf.string(from: date)
        } else if calendar.isDateInYesterday(date) {
            return "Yesterday"
        } else {
            let df = DateFormatter()
            df.dateFormat = "MMM d"
            return df.string(from: date)
        }
    }
}

// MARK: - Email Compose Card

private struct EmailComposeCardData: Equatable {
    let to: String
    let subject: String
    let body: String
    let cc: String?
    let bcc: String?
}

private struct EmailComposeChatCard: View {
    let data: EmailComposeCardData

    @State private var toField: String = ""
    @State private var subjectField: String = ""
    @State private var bodyField: String = ""
    @State private var isSending = false
    @State private var sent = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack(spacing: 8) {
                Image(systemName: "square.and.pencil")
                    .font(.system(size: 16))
                    .foregroundColor(.blue)
                Text("Compose Email")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                Spacer()

                if sent {
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 14))
                            .foregroundColor(.green)
                        Text("Sent")
                            .font(.caption)
                            .foregroundColor(.green)
                    }
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(
                LinearGradient(
                    colors: [Color.blue.opacity(0.25), Color.purple.opacity(0.15)],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )

            if !sent {
                VStack(alignment: .leading, spacing: 10) {
                    // To
                    composeField(label: "To", text: $toField)

                    // Subject
                    composeField(label: "Subject", text: $subjectField)

                    // Body preview
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Body")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.5))

                        Text(bodyField.isEmpty ? "(empty)" : bodyField)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                            .lineLimit(4)
                    }

                    if let error = error {
                        Text(error)
                            .font(.caption2)
                            .foregroundColor(.red)
                    }

                    // Send button
                    Button {
                        Task { await sendEmail() }
                    } label: {
                        HStack(spacing: 6) {
                            if isSending {
                                ProgressView()
                                    .scaleEffect(0.7)
                                    .tint(.white)
                            } else {
                                Image(systemName: "paperplane.fill")
                                    .font(.system(size: 13))
                            }
                            Text(isSending ? "Sending..." : "Send Email")
                                .font(.caption)
                                .fontWeight(.semibold)
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(
                            LinearGradient(
                                colors: [.blue, .purple],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .clipShape(Capsule())
                    }
                    .disabled(isSending || toField.trimmingCharacters(in: .whitespaces).isEmpty)
                    .opacity(toField.trimmingCharacters(in: .whitespaces).isEmpty ? 0.5 : 1)
                }
                .padding(.horizontal, 14)
                .padding(.bottom, 12)
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(red: 0.14, green: 0.11, blue: 0.19))
        )
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.blue.opacity(0.2), lineWidth: 1)
        )
        .onAppear {
            toField = data.to
            subjectField = data.subject
            bodyField = data.body
        }
    }

    private func composeField(label: String, text: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.5))

            TextField(label, text: text)
                .font(.caption)
                .foregroundColor(.white)
                .padding(8)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.white.opacity(0.08))
                )
                .autocapitalization(.none)
        }
    }

    private func sendEmail() async {
        isSending = true
        error = nil

        do {
            let useCase = DependencyContainer.shared.makeSendGmailMessageUseCase()
            _ = try await useCase.execute(
                to: toField,
                subject: subjectField,
                body: bodyField,
                cc: data.cc,
                bcc: data.bcc,
                html: false
            )
            withAnimation { sent = true }
        } catch {
            self.error = error.localizedDescription
        }

        isSending = false
    }
}

// MARK: - Preview

#Preview("User Message") {
    let container = try! ModelContainer(for: Message.self, Conversation.self, configurations: ModelConfiguration(isStoredInMemoryOnly: true))
    return VStack(spacing: 16) {
        MessageBubble(
            message: Message(
                conversationId: UUID(),
                role: "user",
                content: "What's the weather like today?",
                isSynced: true
            )
        )
        MessageBubble(
            message: Message(
                conversationId: UUID(),
                role: "user",
                content: "Can you also check my horoscope for today? I'm a Leo.",
                isSynced: true
            )
        )
    }
    .padding()
    .modelContainer(container)
}

#Preview("Assistant Message") {
    let container = try! ModelContainer(for: Message.self, Conversation.self, configurations: ModelConfiguration(isStoredInMemoryOnly: true))
    return VStack(spacing: 16) {
        MessageBubble(
            message: Message(
                conversationId: UUID(),
                role: "assistant",
                content: "The weather today is sunny with a high of 75°F. Perfect for outdoor activities!",
                category: "weather",
                isSynced: true
            )
        )
        MessageBubble(
            message: Message(
                conversationId: UUID(),
                role: "assistant",
                content: "Leo horoscope for today: The stars are aligned in your favor! Great day for creative pursuits and meeting new people.",
                category: "horoscope",
                isSynced: true
            )
        )
    }
    .padding()
    .modelContainer(container)
}

#Preview("Failed Message") {
    let container = try! ModelContainer(for: Message.self, Conversation.self, configurations: ModelConfiguration(isStoredInMemoryOnly: true))
    return MessageBubble(
        message: Message(
            conversationId: UUID(),
            role: "user",
            content: "This message failed to send",
            isSynced: false
        ),
        onRetry: {}
    )
    .padding()
    .modelContainer(container)
}

#Preview("Long Conversation") {
    let container = try! ModelContainer(for: Message.self, Conversation.self, configurations: ModelConfiguration(isStoredInMemoryOnly: true))
    return ScrollView {
        VStack(spacing: 12) {
            MessageBubble(
                message: Message(
                    conversationId: UUID(),
                    role: "user",
                    content: "Check PNR 2345678901",
                    isSynced: true
                )
            )
            MessageBubble(
                message: Message(
                    conversationId: UUID(),
                    role: "assistant",
                    content: "Your PNR status shows confirmed tickets for Train 12301 Rajdhani Express. Departure: New Delhi at 16:55, Arrival: Howrah at 10:05 next day. Coach: A1, Berth: 23 Lower.",
                    category: "pnr",
                    isSynced: true
                )
            )
            MessageBubble(
                message: Message(
                    conversationId: UUID(),
                    role: "user",
                    content: "What's my tarot reading for this week?",
                    isSynced: true
                )
            )
            MessageBubble(
                message: Message(
                    conversationId: UUID(),
                    role: "assistant",
                    content: "Your tarot card for this week is The Star. This card represents hope, inspiration, and renewal. It suggests that you're entering a period of calm after recent challenges.",
                    category: "tarot",
                    isSynced: true
                )
            )
        }
        .padding()
    }
    .modelContainer(container)
}

#Preview("Category Badges") {
    VStack(spacing: 12) {
        ForEach(["horoscope", "weather", "news", "pnr", "tarot", "numerology", "panchang"], id: \.self) { category in
            let container = try! ModelContainer(for: Message.self, Conversation.self, configurations: ModelConfiguration(isStoredInMemoryOnly: true))
            MessageBubble(
                message: Message(
                    conversationId: UUID(),
                    role: "assistant",
                    content: "Sample response for \(category)",
                    category: category,
                    isSynced: true
                )
            )
            .modelContainer(container)
        }
    }
    .padding()
}
