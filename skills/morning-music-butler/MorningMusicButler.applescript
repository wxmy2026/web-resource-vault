property appleMusicURL : "music://music.apple.com/us/album/one-summers-day-studio-ghibli-favourites-for-solo-piano/1583121575"
property spotifyURI : "spotify:album:6PyXSCnrQoKNQWyrZl4GTs"
property targetVolume : 28

on run
	-- Touch both apps on every launch so first-run setup can surface macOS
	-- Automation permission prompts without starting audio outside the window.
	try
		tell application "Music" to get player state
	end try
	try
		if application "Spotify" is running then tell application "Spotify" to get player state
	end try
	
	set nowDate to current date
	set nowMinutes to (hours of nowDate) * 60 + (minutes of nowDate)
	if nowMinutes < (7 * 60 + 55) or nowMinutes > (8 * 60 + 30) then return
	
	if my tryAppleMusic() then return
	my trySpotify()
end run

on tryAppleMusic()
	try
		open location appleMusicURL
		delay 5
		tell application "Music"
			set sound volume to targetVolume
			play
		end tell
		delay 5
		tell application "Music"
			if player state is playing then return true
		end tell
	on error
		-- Fall through to Spotify.
	end try
	return false
end tryAppleMusic

on trySpotify()
	try
		tell application "Spotify"
			activate
			set sound volume to targetVolume
			set shuffling to true
			play track spotifyURI
		end tell
		delay 5
		tell application "Spotify"
			if player state is playing then return true
		end tell
	on error
		return false
	end try
	return false
end trySpotify
