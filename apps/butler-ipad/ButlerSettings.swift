import Foundation

@MainActor
final class ButlerSettings: ObservableObject {
    @Published var morningMusicEnabled: Bool {
        didSet { defaults.set(morningMusicEnabled, forKey: Keys.morningMusicEnabled) }
    }

    @Published var morningHour: Int {
        didSet { defaults.set(morningHour, forKey: Keys.morningHour) }
    }

    @Published var morningMinute: Int {
        didSet { defaults.set(morningMinute, forKey: Keys.morningMinute) }
    }

    @Published var quietToday: Bool {
        didSet { defaults.set(quietToday, forKey: Keys.quietToday) }
    }

    @Published var activeUntil: Date {
        didSet { defaults.set(activeUntil, forKey: Keys.activeUntil) }
    }

    private let defaults = UserDefaults.standard

    init() {
        morningMusicEnabled = defaults.object(forKey: Keys.morningMusicEnabled) as? Bool ?? true
        morningHour = defaults.object(forKey: Keys.morningHour) as? Int ?? 8
        morningMinute = defaults.object(forKey: Keys.morningMinute) as? Int ?? 0
        quietToday = defaults.object(forKey: Keys.quietToday) as? Bool ?? false
        activeUntil = defaults.object(forKey: Keys.activeUntil) as? Date ?? Calendar.current.date(byAdding: .day, value: 7, to: Date())!
    }

    var morningTime: Date {
        var components = Calendar.current.dateComponents([.year, .month, .day], from: Date())
        components.hour = morningHour
        components.minute = morningMinute
        return Calendar.current.date(from: components) ?? Date()
    }

    func setMorningTime(_ date: Date) {
        let components = Calendar.current.dateComponents([.hour, .minute], from: date)
        morningHour = components.hour ?? 8
        morningMinute = components.minute ?? 0
    }

    func renewWeek() {
        activeUntil = Calendar.current.date(byAdding: .day, value: 7, to: Date()) ?? Date()
        morningMusicEnabled = true
    }

    func markQuietToday() {
        quietToday = true
    }

    func resetDailyFlagsIfNeeded() {
        let stored = defaults.object(forKey: Keys.quietDate) as? Date
        if let stored, Calendar.current.isDateInToday(stored) {
            quietToday = true
        } else {
            quietToday = false
        }
    }

    private enum Keys {
        static let morningMusicEnabled = "morningMusicEnabled"
        static let morningHour = "morningHour"
        static let morningMinute = "morningMinute"
        static let quietToday = "quietToday"
        static let quietDate = "quietDate"
        static let activeUntil = "activeUntil"
    }
}
