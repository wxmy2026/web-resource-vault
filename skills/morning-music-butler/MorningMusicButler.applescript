property personalizedPlaylist : "Morning Music Butler • Favorites Mix"
property appleMusicURL : "music://music.apple.com/us/album/one-summers-day-studio-ghibli-favourites-for-solo-piano/1583121575"
property spotifyURI : "spotify:album:6PyXSCnrQoKNQWyrZl4GTs"
property targetVolume : 28

on run
	-- Touch both apps so first-run setup can surface macOS Automation permission prompts.
	try
		tell application "Music" to get player state
	end try
	try
		if application "Spotify" is running then tell application "Spotify" to get player state
	end try
	
	set nowDate to current date
	set nowMinutes to (hours of nowDate) * 60 + (minutes of nowDate)
	if nowMinutes < (7 * 60 + 55) or nowMinutes > (8 * 60 + 30) then return
	
	-- If the iPad has written today's activity marker, the user is already up and using it.
	if my iPadWasUsedToday() then return
	
	-- Prefer a calm mix rebuilt from favorited tracks in the local Apple Music library.
	if my tryPersonalizedAppleMusic() then return
	-- If there are too few usable favorites, fall back to a known gentle album.
	if my tryAppleMusicFallback() then return
	-- If Apple Music cannot play (subscription/sign-in/catalog issue), try Spotify.
	my trySpotify()
end run

on iPadWasUsedToday()
	set flagPath to POSIX path of (path to home folder) & "Library/Mobile Documents/com~apple~CloudDocs/MorningMusicButler/ipad-active.txt"
	set cmd to "flag=" & quoted form of flagPath & "; [ -f \"$flag\" ] || exit 1; mtime=$(stat -f %m \"$flag\"); midnight=$(date -j -f '%Y-%m-%d' \"$(date +%Y-%m-%d)\" '+%s'); now=$(date '+%s'); [ \"$mtime\" -ge \"$midnight\" ] && [ \"$mtime\" -le \"$now\" ]"
	try
		do shell script cmd
		return true
	on error
		return false
	end try
end iPadWasUsedToday

on tryPersonalizedAppleMusic()
	try
		tell application "Music"
			if exists user playlist personalizedPlaylist then
				set trackCount to count of tracks of user playlist personalizedPlaylist
				if trackCount is greater than or equal to 5 then
					set sound volume to targetVolume
					set shuffle enabled to true
					play user playlist personalizedPlaylist
				else
					return false
				end if
			else
				return false
			end if
		end tell
		delay 5
		tell application "Music"
			if player state is playing then return true
		end tell
	on error
		return false
	end try
	return false
end tryPersonalizedAppleMusic

on tryAppleMusicFallback()
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
end tryAppleMusicFallback

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
