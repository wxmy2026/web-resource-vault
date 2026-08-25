import Foundation
import MusicKit

@MainActor
final class AppleMusicService: ObservableObject {
    enum ConnectionState: String {
        case unknown = "Not connected"
        case denied = "Permission denied"
        case authorized = "Connected"
    }

    @Published private(set) var connectionState: ConnectionState = .unknown
    @Published private(set) var lastMessage: String = ""

    init() {
        refreshAuthorizationState()
    }

    func refreshAuthorizationState() {
        switch MusicAuthorization.currentStatus {
        case .authorized:
            connectionState = .authorized
        case .denied, .restricted:
            connectionState = .denied
        default:
            connectionState = .unknown
        }
    }

    func connect() async {
        let status = await MusicAuthorization.request()
        switch status {
        case .authorized:
            connectionState = .authorized
            lastMessage = "Apple Music is ready for Butler."
        case .denied, .restricted:
            connectionState = .denied
            lastMessage = "Apple Music access was not granted."
        default:
            connectionState = .unknown
            lastMessage = "Apple Music authorization is incomplete."
        }
    }
}
