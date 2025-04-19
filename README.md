# 🎶 Weather-Based Hindi Music Playlist Generator 🇮🇳

> **Automatically curate your Spotify playlist with Hindi songs that match your city’s weather!**

---


This project updates your Spotify playlist with Bollywood/Hindi songs that fit the current weather in your city. Set it up once, and enjoy a fresh, mood-matching playlist every day!

---

## ✨ Features

- 🌤️ **Real-time weather detection** for your city
- 🎵 **Smart Hindi/Bollywood song selection** based on weather mood
- 🎧 **Automatic Spotify playlist updates**
- ⏱️ **Runs on a schedule** (customizable interval)
- 📝 **Playlist name & description** reflect current weather

---

## 📋 Requirements

- Python 3.7+
- Spotify account
- Spotify Developer application credentials
- OpenWeatherMap API key

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/spotify_playlist_generator.git
cd spotify_playlist_generator
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

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
