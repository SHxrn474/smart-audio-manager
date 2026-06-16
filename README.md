# Smart Audio Manager

A lightweight, responsive Python background utility for Windows that automatically pauses your background music (Spotify, YouTube Music, etc.) the exact millisecond you play a video or sound in another application (like VLC or Google Chrome), and seamlessly resumes it once that sound stops.

Unlike standard Windows audio utilities that suffer from a 15-second "audio session decay" delay, this script directly reads real-time decibel peaks from the Windows COM interface to ensure near-instantaneous play/pause response times.

---

## 🚀 Features

* **Instant Response:** Bypasses standard Windows session lags by monitoring direct audio hardware peak values.
* **Smart Browser Handling:** Intentionally isolates your music players from regular web browsers. Watching a YouTube video or Twitch stream in Chrome will successfully pause your music without getting the script confused.
* **Micro-Stutter Protection:** Implements a brief 0.3-second "silence buffer" to make sure your background music doesn't awkwardly unpause during sudden quiet moments in movie dialogue or video stutters.
* **Low Overhead:** Runs quietly in the background using asynchronous loops (`asyncio`), checking audio states 10 times a second with negligible CPU usage.

---

## 🛠️ Prerequisites & Installation

This project requires Windows and Python 3.8+.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/smart-audio-manager.git](https://github.com/YOUR_USERNAME/smart-audio-manager.git)
   cd smart-audio-manager