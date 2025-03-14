from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import logging
import random

app = Flask(__name__)
# Specify CORS to allow requests from your Netlify frontend
CORS(app, resources={
    r"/text-emotion": {"origins": "https://your-site-name.netlify.app"},
    r"/face-emotion": {"origins": "https://your-site-name.netlify.app"}
})

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("Spotify credentials not found in .env")

# Initialize Spotify client
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                              client_secret=SPOTIFY_CLIENT_SECRET))
except Exception as e:
    logging.error(f"Spotify initialization failed: {e}")
    raise

# Load pre-trained model for text emotion with PyTorch explicitly
logging.debug("Attempting to load text emotion analyzer with PyTorch...")
text_emotion_analyzer = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", framework="pt")
logging.debug("Text emotion analyzer loaded successfully")

def detect_text_emotion(text):
    try:
        result = text_emotion_analyzer(text)[0]
        emotion = result["label"]
        confidence = result["score"]
        logging.debug(f"Text emotion: {emotion} (confidence: {confidence:.2f})")
        return {"emotion": emotion, "confidence": confidence, "details": "Analyzed text sentiment"}
    except Exception as e:
        logging.error(f"Text emotion detection error: {e}")
        raise  # Crash the app to diagnose the issue

def detect_face_emotion(image_data):
    # Face detection disabled to reduce memory usage on Render's free tier
    return {"emotion": "neutral", "confidence": 0.5, "details": "Face emotion detection disabled for deployment"}

def recommend_songs(emotion, num_songs=15):
    emotion_queries = {
        "joy": "happy pop upbeat",
        "sadness": "sad pop melancholy",
        "anger": "angry rock intense",
        "fear": "dark pop eerie",
        "surprise": "upbeat pop energetic",
        "disgust": "grunge punk",
        "love": "romantic pop love songs",
        "neutral": "chill pop relaxed",
        "excitement": "dance pop high energy",
        "calm": "acoustic chill",
        "anxiety": "ambient tense",
        "hope": "inspirational pop",
        "frustration": "hard rock aggressive",
        "contentment": "soft pop soothing"
    }
    base_query = emotion_queries.get(emotion.lower(), "chill pop relaxed")
    random_suffix = random.choice(["", "2020s", "classic", "indie", "mix"])
    query = f"{base_query} {random_suffix}".strip()
    logging.debug(f"Searching Spotify with query: {query}")
    
    try:
        offset = random.randint(0, 100)
        results = sp.search(q=query, type="track", limit=50, offset=offset)
        tracks = results["tracks"]["items"]
        
        random.shuffle(tracks)
        song_recommendations = [
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "url": track["external_urls"]["spotify"],
                "preview_url": track["preview_url"],
                "album_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                "artist_image": track["artists"][0]["images"][0]["url"] if track["artists"][0].get("images") else None
            }
            for track in tracks[:num_songs]
        ]
        logging.debug(f"Recommended songs: {song_recommendations}")
        return song_recommendations if song_recommendations else [{"name": "No songs found", "artist": "", "url": "", "preview_url": None, "album_image": None, "artist_image": None}]
    except Exception as e:
        logging.error(f"Spotify error: {e}")
        return [{"name": f"Error fetching songs: {str(e)}", "artist": "", "url": "", "preview_url": None, "album_image": None, "artist_image": None}]

@app.route("/text-emotion", methods=["POST"])
def text_emotion():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    emotion_data = detect_text_emotion(text)
    songs = recommend_songs(emotion_data["emotion"])
    response = {
        "emotion": emotion_data["emotion"],
        "confidence": emotion_data["confidence"],
        "details": emotion_data["details"],
        "songs": songs
    }
    logging.debug(f"Text emotion response: {response}")
    return jsonify(response)

@app.route("/face-emotion", methods=["POST"])
def face_emotion():
    data = request.json
    image_data = data.get("image", "")
    if not image_data:
        return jsonify({"error": "No image provided"}), 400
    emotion_data = detect_face_emotion(image_data)
    songs = recommend_songs(emotion_data["emotion"])
    response = {
        "emotion": emotion_data["emotion"],
        "confidence": emotion_data["confidence"],
        "details": emotion_data["details"],
        "songs": songs
    }
    logging.debug(f"Face emotion response: {response}")
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)