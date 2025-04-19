# Weather-Based Hindi Music Playlist Generator

This application automatically updates a Spotify playlist with Hindi songs that match the current weather in your city. It runs on a schedule and continuously updates your playlist with mood-appropriate music.

![Playlist Generator Demo](https://via.placeholder.com/800x400?text=Hindi+Music+Playlist+Generator)

## ✨ Features

- 🌤️ Fetches real-time weather data for your location
- 🎵 Selects Hindi/Bollywood songs based on weather mood
- 🎧 Automatically updates a Spotify playlist
- ⏱️ Runs on a schedule (configurable update interval)
- 📋 Updates playlist name and description with current weather information

## 📋 Requirements

- Python 3.7+
- Spotify account
- Spotify Developer application credentials
- OpenWeatherMap API key

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/spotify_playlist_generator.git
cd spotify_playlist_generator
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory and configure it as shown in the template below.

---

## 📄 `.env` File Template

```plaintext
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key

# App Configuration
REDIRECT_URI=http://localhost:8888/callback
```

> ⚠️ **Important**: Never share your `.env` file or API credentials publicly.

---

## 🏃‍♂️ Running the App

1. **Start the Application**:
    ```bash
    python app.py
    ```

2. Open your browser and navigate to the provided URL to interact with the app.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

Happy playlist generating! 🎵