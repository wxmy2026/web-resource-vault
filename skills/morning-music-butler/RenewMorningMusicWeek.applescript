on run
	set stateDir to POSIX path of (path to home folder) & "Library/Application Support/MorningMusicButler/"
	set renewScript to stateDir & "renew-week.sh"
	try
		do shell script "/bin/bash " & quoted form of renewScript
		display notification "未来 7 个早晨已重新启用，并刷新了收藏偏好。" with title "Morning Music Butler"
	on error errText
		display dialog "续一周失败：" & errText buttons {"好"} default button 1 with icon stop
	end try
end run
