import os
import time
import json
import numpy as np
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")
CITY = os.getenv("CITY", "Rohtak")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "3600"))  # in seconds, default 1 hour

# Comprehensive list of popular Hindi/Bollywood artists for better filtering
HINDI_ARTISTS = [
    "Arijit Singh", "Shreya Ghoshal", "Sonu Nigam", "Neha Kakkar", "Badshah",
    "Atif Aslam", "A.R. Rahman", "Lata Mangeshkar", "Kishore Kumar", "Mohammed Rafi",
    "Kumar Sanu", "Alka Yagnik", "Udit Narayan", "Jubin Nautiyal", "Honey Singh",
    "Vishal Dadlani", "Shaan", "KK", "Shankar Mahadevan", "Pritam",
    "Amit Trivedi", "Diljit Dosanjh", "Sunidhi Chauhan", "Monali Thakur", "Armaan Malik",
    "Darshan Raval", "Shilpa Rao", "Vishal Mishra", "Tulsi Kumar", "Dhvani Bhanushali"
]

# Popular Hindi Music Playlists on Spotify for mining additional tracks
HINDI_PLAYLIST_IDS = [
    "37i9dQZF1DX0XUoa6ej4Ks",  # Bollywood Butter
    "37i9dQZF1DX7cLxqtNO3zl",  # Bollywood Soft Pop
    "37i9dQZF1DX6koKzb5Nscm",  # Bollywood Romance
    "37i9dQZF1DX3omgz2xDUdX",  # Bollywood Mellow
    "37i9dQZF1DXa9wYJr1oMQU",  # Bollywood Party
]

# Enhanced weather to Hindi music mood mapping with audio features targets
WEATHER_MOOD_MAP = {
    # Clear weather
    "clear sky": {
        "mood": "cheerful",
        "keywords": ["hindi happy songs", "bollywood upbeat", "hindi party songs", "desi beats"],
        "audio_features": {
            "target_values": {"energy": 0.8, "valence": 0.8, "danceability": 0.8, "tempo": 125, "acousticness": 0.2},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 20, "acousticness": 0.2},
            "weights": {"energy": 0.3, "valence": 0.3, "danceability": 0.2, "tempo": 0.1, "acousticness": 0.1}
        }
    },
    "few clouds": {
        "mood": "pleasant",
        "keywords": ["hindi melodious songs", "bollywood romantic", "hindi chill music", "bollywood feel good"],
        "audio_features": {
            "target_values": {"energy": 0.6, "valence": 0.7, "danceability": 0.6, "tempo": 110, "acousticness": 0.4},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 20, "acousticness": 0.2},
            "weights": {"energy": 0.25, "valence": 0.3, "danceability": 0.25, "tempo": 0.1, "acousticness": 0.1}
        }
    },

    # Cloudy weather
    "scattered clouds": {
        "mood": "thoughtful",
        "keywords": ["hindi soft songs", "bollywood soothing", "indian acoustic", "hindi melodious"],
        "audio_features": {
            "target_values": {"energy": 0.5, "valence": 0.6, "danceability": 0.5, "tempo": 95, "acousticness": 0.5},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.3, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.3}
        }
    },
    "broken clouds": {
        "mood": "nostalgic",
        "keywords": ["hindi nostalgia", "bollywood classics", "old hindi songs", "retro bollywood"],
        "audio_features": {
            "target_values": {"energy": 0.5, "valence": 0.5, "danceability": 0.4, "tempo": 90, "acousticness": 0.6},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.3, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.3}
        }
    },
    "overcast clouds": {
        "mood": "melancholic",
        "keywords": ["hindi sad songs", "bollywood emotional", "indian melancholy", "hindi introspective"],
        "audio_features": {
            "target_values": {"energy": 0.4, "valence": 0.3, "danceability": 0.4, "tempo": 85, "acousticness": 0.7},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.3, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.3}
        }
    },

    # Rain
    "light rain": {
        "mood": "romantic",
        "keywords": ["hindi rain songs", "bollywood romantic", "indian monsoon music", "baarish songs"],
        "audio_features": {
            "target_values": {"energy": 0.5, "valence": 0.6, "danceability": 0.5, "tempo": 90, "acousticness": 0.6},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.3, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.3}
        }
    },
    "moderate rain": {
        "mood": "emotional",
        "keywords": ["hindi emotional songs", "bollywood sad", "hindi soulful", "hindi rain ballads"],
        "audio_features": {
            "target_values": {"energy": 0.5, "valence": 0.4, "danceability": 0.4, "tempo": 85, "acousticness": 0.7},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.3, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.3}
        }
    },
    "heavy rain": {
        "mood": "dramatic",
        "keywords": ["hindi dramatic songs", "bollywood intense", "indian classical fusion", "hindi powerful ballads"],
        "audio_features": {
            "target_values": {"energy": 0.7, "valence": 0.4, "danceability": 0.4, "tempo": 90, "acousticness": 0.5},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.3, "valence": 0.2, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.3}
        }
    },
    "thunderstorm": {
        "mood": "intense",
        "keywords": ["hindi rock", "bollywood intense", "indian fusion", "hindi powerful songs"],
        "audio_features": {
            "target_values": {"energy": 0.8, "valence": 0.3, "danceability": 0.5, "tempo": 120, "acousticness": 0.3},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 20, "acousticness": 0.2},
            "weights": {"energy": 0.3, "valence": 0.2, "danceability": 0.1, "tempo": 0.2, "acousticness": 0.2}
        }
    },

    # Snow
    "light snow": {
        "mood": "serene",
        "keywords": ["hindi peaceful songs", "bollywood ambient", "indian instrumental", "hindi calming music"],
        "audio_features": {
            "target_values": {"energy": 0.3, "valence": 0.6, "danceability": 0.3, "tempo": 70, "acousticness": 0.8},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.2, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.4}
        }
    },
    "snow": {
        "mood": "peaceful",
        "keywords": ["hindi devotional", "indian classical", "bollywood soothing", "hindi winter songs"],
        "audio_features": {
            "target_values": {"energy": 0.3, "valence": 0.5, "danceability": 0.3, "tempo": 65, "acousticness": 0.8},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.2, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.4}
        }
    },

    # Other conditions
    "mist": {
        "mood": "mysterious",
        "keywords": ["hindi atmospheric", "bollywood mysterious", "indian fusion ambient", "hindi mellow"],
        "audio_features": {
            "target_values": {"energy": 0.4, "valence": 0.4, "danceability": 0.4, "tempo": 80, "acousticness": 0.7},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.2, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.4}
        }
    },
    "fog": {
        "mood": "mysterious",
        "keywords": ["hindi atmospheric", "bollywood mysterious", "indian fusion ambient", "hindi mellow"],
        "audio_features": {
            "target_values": {"energy": 0.4, "valence": 0.4, "danceability": 0.4, "tempo": 80, "acousticness": 0.7},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.2, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.4}
        }
    },

    # Temperature-based conditions (will be used if no weather description matches)
    "hot": {
        "mood": "summer",
        "keywords": ["hindi summer songs", "bollywood dance", "indian hot weather songs", "desi party"],
        "audio_features": {
            "target_values": {"energy": 0.8, "valence": 0.7, "danceability": 0.8, "tempo": 125, "acousticness": 0.2},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 20, "acousticness": 0.2},
            "weights": {"energy": 0.3, "valence": 0.2, "danceability": 0.3, "tempo": 0.1, "acousticness": 0.1}
        }
    },
    "cold": {
        "mood": "cozy",
        "keywords": ["hindi winter songs", "bollywood soothing", "indian slow music", "hindi cozy songs"],
        "audio_features": {
            "target_values": {"energy": 0.4, "valence": 0.5, "danceability": 0.4, "tempo": 80, "acousticness": 0.7},
            "ranges": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 15, "acousticness": 0.2},
            "weights": {"energy": 0.2, "valence": 0.2, "danceability": 0.1, "tempo": 0.1, "acousticness": 0.4}
        }
    },

    # Default
    "default": {
        "mood": "general",
        "keywords": ["popular hindi songs", "bollywood hits", "hindi top songs", "trending bollywood"],
        "audio_features": {
            "target_values": {"energy": 0.6, "valence": 0.6, "danceability": 0.6, "tempo": 100, "acousticness": 0.5},
            "ranges": {"energy": 0.3, "valence": 0.3, "danceability": 0.3, "tempo": 25, "acousticness": 0.3},
            "weights": {"energy": 0.2, "valence": 0.2, "danceability": 0.2, "tempo": 0.2, "acousticness": 0.2}
        }
    }
}


def get_current_weather(city):
    """Get current weather for a city with enhanced data"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        weather_desc = data["weather"][0]["description"].lower()

        return {
            "description": weather_desc,
            "main": data["weather"][0]["main"].lower(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "clouds": data.get("clouds", {}).get("all", 0),
            "rain": data.get("rain", {}).get("1h", 0) if "rain" in data else 0,
            "time": datetime.now().hour,
            "raw_data": data  # Store raw data for detailed analysis
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None


def get_enhanced_mood_from_weather(weather_data):
    """
    Enhanced mood determination based on detailed weather analysis
    Incorporates multiple parameters and normalized values
    """
    if not weather_data:
        return WEATHER_MOOD_MAP["default"]

    weather_desc = weather_data["description"]
    weather_main = weather_data["main"]
    temp = weather_data["temperature"]
    clouds = weather_data["clouds"]
    rain_amount = weather_data["rain"]
    time_of_day = weather_data["time"]

    # Check for exact weather description match
    for key in WEATHER_MOOD_MAP:
        if key in weather_desc:
            print(f"Weather match found: {key}")
            return WEATHER_MOOD_MAP[key]

    # Check for weather main type
    if "thunderstorm" in weather_main:
        return WEATHER_MOOD_MAP["thunderstorm"]
    elif "snow" in weather_main:
        return WEATHER_MOOD_MAP["snow"] if rain_amount > 1 else WEATHER_MOOD_MAP["light snow"]
    elif "rain" in weather_main:
        if rain_amount > 7:
            return WEATHER_MOOD_MAP["heavy rain"]
        elif rain_amount > 2.5:
            return WEATHER_MOOD_MAP["moderate rain"]
        else:
            return WEATHER_MOOD_MAP["light rain"]
    elif "drizzle" in weather_main:
        return WEATHER_MOOD_MAP["light rain"]
    elif "mist" in weather_main or "fog" in weather_main:
        return WEATHER_MOOD_MAP["mist"]
    elif "clouds" in weather_main:
        if clouds > 80:
            return WEATHER_MOOD_MAP["overcast clouds"]
        elif clouds > 50:
            return WEATHER_MOOD_MAP["broken clouds"]
        else:
            return WEATHER_MOOD_MAP["scattered clouds"]
    elif "clear" in weather_main:
        if temp > 30:
            return WEATHER_MOOD_MAP["hot"]
        elif temp < 10:
            return WEATHER_MOOD_MAP["cold"]
        else:
            return WEATHER_MOOD_MAP["clear sky"] if clouds < 10 else WEATHER_MOOD_MAP["few clouds"]

    # Temperature-based fallback
    if temp > 30:
        return WEATHER_MOOD_MAP["hot"]
    elif temp < 10:
        return WEATHER_MOOD_MAP["cold"]

    # Default mood if no match
    return WEATHER_MOOD_MAP["default"]


def authenticate_spotify():
    """Authenticate with Spotify API with improved error handling"""
    scope = "playlist-modify-public playlist-modify-private user-read-private"
    try:
        # Use cache handling with a clear name
        cache_path = ".spotify_token_cache"

        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            cache_path=cache_path,
            open_browser=True  # Ensure this matches your environment
        )

        # Force token refresh to ensure we have a valid token
        token_info = auth_manager.get_cached_token()
        if not token_info or auth_manager.is_token_expired(token_info):
            print("Getting new token...")
            auth_manager.get_access_token(as_dict=False)

        # Create Spotify client with the auth manager
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Test the connection with a simple API call
        current_user = sp.current_user()
        print(f"Successfully authenticated as: {current_user['display_name']}")

        return sp
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_audio_features_batch(sp, track_ids):
    """Get audio features with explicit token handling"""
    if not track_ids:
        return []

    if not sp:
        print("Error: Spotify client is None")
        return []

    try:
        # Make sure we have small enough batches
        batch_size = 20  # Even smaller batch to troubleshoot
        all_features = []

        # Process in smaller batches with explicit error handling
        for i in range(0, len(track_ids), batch_size):
            chunk = track_ids[i:i + batch_size]
            chunk_ids = ",".join(chunk)
            print(f"Processing batch {i // batch_size + 1} with {len(chunk)} tracks")

            try:
                # Check that our client still has a valid token
                if not hasattr(sp, '_auth'):
                    print("Warning: Spotify client has no auth attribute")
                    return []

                # Try getting features with explicit token checking
                features = sp.audio_features(chunk)

                if features:
                    valid_features = [f for f in features if f]
                    all_features.extend(valid_features)
                    print(f"Got {len(valid_features)} valid features from batch")
                else:
                    print("No features returned for batch")

            except spotipy.SpotifyException as e:
                print(f"Spotify API error in batch {i // batch_size + 1}: {e}")
                if "token" in str(e).lower() or "unauthorized" in str(e).lower():
                    print("Token seems invalid - stopping processing")
                    return []
            except Exception as e:
                print(f"General error in batch {i // batch_size + 1}: {e}")

        return all_features

    except Exception as e:
        print(f"Error in audio features function: {e}")
        return []

def is_hindi_track(track):
    """
    Enhanced detection of Hindi tracks using multiple signals
    """
    if not track:
        return False

    # Check artist names against known Hindi artists
    artists = [artist["name"] for artist in track.get("artists", [])]

    # Direct match with our list of Hindi artists
    for artist in artists:
        if any(hindi_artist.lower() in artist.lower() for hindi_artist in HINDI_ARTISTS):
            return True

    # Check track name for Hindi keywords
    track_name = track.get("name", "").lower()
    hindi_keywords = ["bollywood", "hindi", "desi", "bhangra", "punjabi",
                      "indian", "dil", "pyaar", "ishq", "sanam", "tum",
                      "tera", "mera", "tu ", "main", "jaan", "kyun", "hai"]

    if any(keyword in track_name for keyword in hindi_keywords):
        return True

    # Check if album has Hindi indicators
    album_name = track.get("album", {}).get("name", "").lower()
    if any(keyword in album_name for keyword in ["bollywood", "hindi", "desi", "indian"]):
        return True

    return False


def get_audio_features_batch(sp, track_ids):
    """Get audio features for multiple tracks at once"""
    if not track_ids:
        return []

    try:
        # Batch track IDs into chunks of 100 (Spotify API limit)
        all_features = []
        for i in range(0, len(track_ids), 100):
            chunk = track_ids[i:i+100]
            print(f"Fetching audio features for batch of {len(chunk)} tracks")
            features = sp.audio_features(chunk)
            if features:
                all_features.extend(features)
        return all_features
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error getting audio features: {e}")
        # Check if token expired
        if "token" in str(e).lower():
            print("Token may have expired, try re-authenticating")
            # You could implement re-authentication here
        return []
    except Exception as e:
        print(f"Error getting audio features: {e}")
        return []


def calculate_track_score(track_features, target_features):
    """
    Calculate a similarity score between track audio features and target features
    using cosine similarity and weighted feature importance
    """
    if not track_features:
        return 0

    # Extract the relevant features we need
    track_vector = []
    target_vector = []
    weights = []

    for feature, target_value in target_features["target_values"].items():
        if feature in track_features and track_features[feature] is not None:
            feature_range = target_features["ranges"].get(feature, 0.2)
            weight = target_features["weights"].get(feature, 0.2)

            track_vector.append(track_features[feature])
            target_vector.append(target_value)
            weights.append(weight)

    if not track_vector:
        return 0

    # Convert to numpy arrays
    track_array = np.array(track_vector).reshape(1, -1)
    target_array = np.array(target_vector).reshape(1, -1)
    weights_array = np.array(weights)

    # Calculate weighted cosine similarity
    similarity = cosine_similarity(track_array, target_array)[0][0]

    # Add popularity factor (scale 0-100 to 0-1)
    popularity = track_features.get("popularity", 50) / 100

    # Final score is a weighted combination of similarity and popularity
    final_score = (similarity * 0.7) + (popularity * 0.3)

    return final_score


def search_and_rank_hindi_tracks_alternative(sp, mood_info, limit=25):
    """Alternative approach without relying on audio_features endpoint"""
    mood = mood_info["mood"]
    keywords = mood_info["keywords"]

    all_tracks = []
    used_track_names = set()

    # Search by each keyword
    for keyword in keywords:
        query = f"{keyword}"
        try:
            results = sp.search(q=query, type="track", limit=20, market="IN")

            for item in results["tracks"]["items"]:
                track_name = item["name"].lower()

                if track_name in used_track_names:
                    continue

                if is_hindi_track(item):
                    # Instead of using audio_features, use track properties directly
                    # This avoids the problematic endpoint
                    popularity = item.get("popularity", 50)
                    explicit = item.get("explicit", False)
                    duration = item.get("duration_ms", 0) / 1000  # convert to seconds

                    # Simple scoring method without audio features
                    # Higher popularity is better
                    score = popularity / 100.0

                    # Penalize extremely short or long tracks slightly
                    if duration < 60 or duration > 480:
                        score *= 0.9

                    # Create a simpler track record
                    all_tracks.append({
                        "track": item,
                        "score": score
                    })

                    used_track_names.add(track_name)

                if len(all_tracks) >= limit * 2:
                    break
        except Exception as e:
            print(f"Error searching for '{keyword}': {e}")
            continue

    # If we don't have enough tracks, try playlists
    if len(all_tracks) < limit:
        print("Not enough tracks found, searching playlists...")
        for playlist_id in HINDI_PLAYLIST_IDS:
            try:
                playlist_tracks = sp.playlist_tracks(playlist_id, limit=20, market="IN")

                for item in playlist_tracks["items"]:
                    track = item.get("track")
                    if track:
                        track_name = track["name"].lower()
                        if track_name not in used_track_names and is_hindi_track(track):
                            # Simple scoring
                            popularity = track.get("popularity", 50)
                            score = popularity / 100.0

                            all_tracks.append({
                                "track": track,
                                "score": score
                            })
                            used_track_names.add(track_name)
            except Exception as e:
                print(f"Error fetching playlist {playlist_id}: {e}")

            if len(all_tracks) >= limit * 2:
                break

    # Sort by score
    all_tracks.sort(key=lambda x: x["score"], reverse=True)

    # Get track IDs
    best_track_ids = [item["track"]["id"] for item in all_tracks[:limit]]

    print(f"Found and scored {len(all_tracks)} Hindi tracks using alternative method")
    return best_track_ids

def update_playlist(sp, playlist_id, track_ids):
    """Update a Spotify playlist with new tracks"""
    try:
        # Get playlist details
        playlist_info = sp.playlist(playlist_id)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Update playlist name to reflect current weather and time
        weather_data = get_current_weather(CITY)
        mood_info = get_enhanced_mood_from_weather(weather_data)

        new_name = f"Hindi {mood_info['mood'].title()} Music • {CITY} • {current_time}"
        new_description = f"Hindi music for {weather_data['description']} weather in {CITY}. Updated on {current_time}."

        # Update playlist metadata
        sp.playlist_change_details(
            playlist_id=playlist_id,
            name=new_name,
            description=new_description
        )

        # Clear current playlist
        sp.playlist_replace_items(playlist_id, [])

        # Add new tracks
        # Spotify API accepts max 100 tracks per request
        chunks = [track_ids[i:i + 100] for i in range(0, len(track_ids), 100)]
        for chunk in chunks:
            sp.playlist_add_items(playlist_id, chunk)

        print(f"Successfully updated playlist '{new_name}' with {len(track_ids)} Hindi tracks")
        return True
    except Exception as e:
        print(f"Error updating playlist: {e}")
        return False


def generate_weather_report(weather_data):
    """Generate a detailed weather report"""
    if not weather_data:
        return "Weather data unavailable"

    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    wind_speed = weather_data["wind_speed"]
    clouds = weather_data["clouds"]
    description = weather_data["description"].title()
    time_of_day = "Morning" if 5 <= weather_data["time"] < 12 else "Afternoon" if 12 <= weather_data[
        "time"] < 17 else "Evening" if 17 <= weather_data["time"] < 21 else "Night"

    report = f"""
Weather Report for {CITY} ({time_of_day}):
• Condition: {description}
• Temperature: {temp:.1f}°C
• Humidity: {humidity}%
• Wind Speed: {wind_speed} m/s
• Cloud Cover: {clouds}%
"""
    return report

def main():
    print(f"Starting Enhanced Weather-Based Hindi Music Spotify Playlist Updater for {CITY}")

    # Initial authentication
    sp = authenticate_spotify()
    if not sp:
        print("Failed to authenticate with Spotify. Exiting.")
        return

    # Check playlist ID
    try:
        playlist_info = sp.playlist(PLAYLIST_ID)
        print(f"Connected to playlist: {playlist_info['name']}")
    except Exception as e:
        print(f"Error connecting to playlist: {e}")
        return

    # Main loop
    while True:
        try:
            print("\n" + "=" * 50)
            print(f"Updating playlist at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Re-authenticate on each iteration to avoid token issues
            sp = authenticate_spotify()
            if not sp:
                print("Failed to re-authenticate. Waiting 60 seconds...")
                time.sleep(60)
                continue

            # Get weather
            weather_data = get_current_weather(CITY)
            if not weather_data:
                print("Failed to get weather data")
                time.sleep(60)
                continue

            # Print weather report
            print(generate_weather_report(weather_data))

            # Get mood
            mood_info = get_enhanced_mood_from_weather(weather_data)
            print(f"Selected mood: {mood_info['mood']}")
            print(f"Keywords: {', '.join(mood_info['keywords'])}")

            # Use alternative approach that doesn't rely on audio_features
            # Changed limit to 25 tracks as requested
            track_ids = search_and_rank_hindi_tracks_alternative(sp, mood_info, limit=25)

            if track_ids:
                # Update playlist
                success = update_playlist(sp, PLAYLIST_ID, track_ids)
                if success:
                    print(f"Hindi music playlist updated successfully!")
                else:
                    print("Failed to update playlist")
            else:
                print("No Hindi tracks found for the current mood")

            # Wait for next update
            print(f"Next update in {UPDATE_INTERVAL // 60} minutes...")
            time.sleep(UPDATE_INTERVAL)

        except Exception as e:
            print(f"Error in main loop: {e}")
            print("Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()