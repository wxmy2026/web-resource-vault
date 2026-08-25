property mixName : "Morning Music Butler • Favorites Mix"

on run
	tell application "Music"
		try
			if exists user playlist mixName then delete user playlist mixName
		end try
		set morningMix to make new user playlist with properties {name:mixName}
		set addedCount to 0
		set libraryTracks to every track of library playlist 1
		repeat with aTrack in libraryTracks
			set isFavorite to false
			try
				set isFavorite to favorited of aTrack
			on error
				try
					set isFavorite to loved of aTrack
				end try
			end try
			if isFavorite then
				set isGentle to false
				try
					set g to (genre of aTrack) as text
					ignoring case
						if g contains "ambient" or g contains "classical" or g contains "soundtrack" or g contains "instrumental" or g contains "easy listening" or g contains "new age" or g contains "piano" or g contains "acoustic" or g contains "jazz" or g contains "folk" or g contains "原声" or g contains "古典" or g contains "器乐" or g contains "钢琴" or g contains "爵士" then set isGentle to true
					end ignoring
				end try
				if isGentle is false then
					try
						set tempoValue to bpm of aTrack
						if tempoValue is greater than 0 and tempoValue is less than or equal to 105 then set isGentle to true
					end try
				end if
				if isGentle then
					try
						duplicate aTrack to morningMix
						set addedCount to addedCount + 1
					end try
				end if
			end if
		end repeat
		return addedCount
	end tell
end run
