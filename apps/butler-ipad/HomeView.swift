import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var settings: ButlerSettings
    @EnvironmentObject private var music: AppleMusicService

    var body: some View {
        NavigationStack {
            Form {
                Section("Morning Music") {
                    Toggle("Enabled", isOn: $settings.morningMusicEnabled)

                    DatePicker(
                        "Time",
                        selection: Binding(
                            get: { settings.morningTime },
                            set: { settings.setMorningTime($0) }
                        ),
                        displayedComponents: .hourAndMinute
                    )

                    LabeledContent("Runs until") {
                        Text(settings.activeUntil, style: .date)
                    }

                    Button("Quiet today") {
                        settings.markQuietToday()
                    }
                    .disabled(settings.quietToday)

                    Button("Run another week") {
                        settings.renewWeek()
                    }
                }

                Section("Music") {
                    LabeledContent("Apple Music", value: music.connectionState.rawValue)

                    Button("Connect Apple Music") {
                        Task { await music.connect() }
                    }

                    if !music.lastMessage.isEmpty {
                        Text(music.lastMessage)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }

                Section("Butler") {
                    Text("Local-first. New skills will appear here instead of becoming separate apps.")
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Butler")
            .task {
                settings.resetDailyFlagsIfNeeded()
                music.refreshAuthorizationState()
            }
        }
    }
}
