import SwiftUI

@main
struct ButlerApp: App {
    @StateObject private var settings = ButlerSettings()
    @StateObject private var music = AppleMusicService()

    var body: some Scene {
        WindowGroup {
            HomeView()
                .environmentObject(settings)
                .environmentObject(music)
        }
    }
}
