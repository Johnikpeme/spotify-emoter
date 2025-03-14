from flask import Flask, request, jsonify
from flask_cors import CORS
import text2emotion as te
import nltk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import logging
import random

# Download required NLTK data at startup
logging.basicConfig(level=logging.DEBUG)
logging.debug("Downloading NLTK data...")
try:
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    logging.debug("NLTK data downloaded successfully")
except Exception as e:
    logging.error(f"Failed to download NLTK data: {e}")
    raise

app = Flask(__name__)
CORS(app, resources={
    r"/text-emotion": {"origins": "https://your-site-name.netlify.app"},
    r"/face-emotion": {"origins": "https://your-site-name.netlify.app"}
})

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    logging.error("Spotify credentials not found in .env")
    raise ValueError("Spotify credentials not found in .env")

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                              client_secret=SPOTIFY_CLIENT_SECRET))
    logging.debug("Spotify client initialized successfully")
except Exception as e:
    logging.error(f"Spotify initialization failed: {e}")
    raise

logging.debug("text2emotion is ready for text emotion analysis")

def detect_text_emotion(text):
    try:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Invalid text input")
        
        emotions = te.get_emotion(text)
        logging.debug(f"Raw emotions from text2emotion: {emotions}")
        
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]
        
        if confidence == 0:
            logging.warning(f"No emotion detected for text: '{text}', emotions: {emotions}")
            return {"emotion": "neutral", "confidence": 0.5, "details": "No emotion detected"}
        
        logging.debug(f"Text emotion: {dominant_emotion} (confidence: {confidence:.2f})")
        return {
            "emotion": dominant_emotion.lower(),
            "confidence": confidence,
            "details": f"Analyzed text sentiment with text2emotion: {emotions}"
        }
    except Exception as e:
        logging.error(f"Text emotion detection error: {e}")
        return {"emotion": "neutral", "confidence": 0.5, "details": "Error in text analysis"}

def detect_face_emotion(image_data):
    return {"emotion": "neutral", "confidence": 0.5, "details": "Face emotion detection disabled for deployment"}

def recommend_songs(emotion, num_songs=15):
    emotion_queries = {
        "happy": "happy pop upbeat",
        "sad": "sad pop melancholy",
        "angry": "angry rock intense",
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
        if not tracks:
            logging.warning(f"No tracks found for query: {query}")
            return [{"name": "No songs found", "artist": "", "url": "", "preview_url": None, "album_image": None, "artist_image": None}]
        
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
        return song_recommendations
    except Exception as e:
        logging.error(f"Spotify error: {e}")
        return [{"name": f"Error fetching songs: {str(e)}", "artist": "", "url": "", "preview_url": None, "album_image": None, "artist_image": None}]

@app.route("/text-emotion", methods=["POST"])
def text_emotion():
    try:
        data = request.json
        if not data or "text" not in data:
            logging.error("No text provided in request")
            return jsonify({"error": "No text provided"}), 400
        
        text = data.get("text", "").strip()
        if not text:
            logging.error("Empty text provided in request")
            return jsonify({"error": "Empty text provided"}), 400
        
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
    except Exception as e:
        logging.error(f"Error in /text-emotion endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/face-emotion", methods=["POST"])
def face_emotion():
    try:
        data = request.json
        if not data or "image" not in data:
            logging.error("No image provided in request")
            return jsonify({"error": "No image provided"}), 400
        
        image_data = data.get("image", "").strip()
        if not image_data:
            logging.error("Empty image provided in request")
            return jsonify({"error": "Empty image provided"}), 400
        
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
    except Exception as e:
        logging.error(f"Error in /face-emotion endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)