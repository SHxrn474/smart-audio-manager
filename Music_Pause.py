import asyncio
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus

# Broad keywords to catch both Audio Mixer processes AND Media Control session IDs
# "youtube" catches both "youtube music.exe" and the browser PWA
MUSIC_KEYWORDS = ["spotify", "chrome", "msedge", "youtube", "brave", "firefox"]

async def pause_music():
    manager = await MediaManager.request_async()
    sessions = manager.get_sessions()
    did_pause = False
    
    for session in sessions:
        # e.g., "Google.Chrome" or "SpotifyAB.SpotifyMusic"
        app_name = session.source_app_user_model_id.lower() 
        
        # If any of our keywords (like "chrome" or "spotify") are in the app name
        if any(keyword in app_name for keyword in MUSIC_KEYWORDS):
            info = session.get_playback_info()
            if info and info.playback_status == PlaybackStatus.PLAYING:
                print(f"  -> ⏸️ Pausing: {session.source_app_user_model_id}")
                await session.try_pause_async()
                did_pause = True
                
    return did_pause

async def play_music():
    manager = await MediaManager.request_async()
    sessions = manager.get_sessions()
    
    for session in sessions:
        app_name = session.source_app_user_model_id.lower()
        if any(keyword in app_name for keyword in MUSIC_KEYWORDS):
            info = session.get_playback_info()
            if info and info.playback_status != PlaybackStatus.PLAYING:
                print(f"  -> ▶️ Resuming: {session.source_app_user_model_id}")
                await session.try_play_async()

def get_interrupting_apps():
    sessions = AudioUtilities.GetAllSessions()
    interrupting_apps = []

    for session in sessions:
        if session.Process:
            # e.g., "vlc.exe", "chrome.exe"
            app_name = session.Process.name().lower()
            
            # Check if it's a music app
            is_music_app = any(keyword in app_name for keyword in MUSIC_KEYWORDS)
            
            if not is_music_app:
                try:
                    meter = session._ctl.QueryInterface(IAudioMeterInformation)
                    peak_value = meter.GetPeakValue()
                    
                    # THRESHOLD: > 0.01 (1% volume)
                    # This completely ignores the silent "audio decay" when VLC pauses
                    if peak_value > 0.01:
                        interrupting_apps.append(app_name)
                except Exception:
                    pass
                    
    return interrupting_apps

async def main_loop():
    music_was_auto_paused = False
    silence_counter = 0
    
    print("🎧 Smart Audio Manager [Final Version] Active.")
    print("Listening for live audio peaks...\n")
    
    while True:
        interrupting_apps = get_interrupting_apps()

        # SCENARIO 1: An interrupting app (VLC, Games, etc.) makes noticeable sound
        if interrupting_apps:
            silence_counter = 0 
            if not music_was_auto_paused:
                print(f"\n🔊 Live sound detected from: {', '.join(interrupting_apps)}")
                if await pause_music():
                    music_was_auto_paused = True
            
            # Brief pause to let commands process
            await asyncio.sleep(0.3) 

        # SCENARIO 2: The interrupting apps go quiet
        else:
            if music_was_auto_paused:
                silence_counter += 1
                
                # Only wait 3 loops (0.3 seconds) of total silence to ensure it wasn't a micro-stutter
                if silence_counter >= 3:
                    print("\n🔇 Interrupting apps went quiet.")
                    await play_music()
                    music_was_auto_paused = False
                    silence_counter = 0

        # Run checks 10 times a second for near-instant response times
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\nExiting Audio Manager. Goodbye!")