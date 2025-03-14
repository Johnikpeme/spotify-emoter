import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  CardMedia,
  Grid,
  CircularProgress,
  Box,
  IconButton,
  Switch,
  createTheme,
  ThemeProvider,
} from "@mui/material";
import Webcam from "react-webcam";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import "./styles.css";

// Create a custom Material-UI theme to enforce Sora font
const theme = createTheme({
  typography: {
    fontFamily: "'Sora', sans-serif",
    allVariants: {
      fontFamily: "'Sora', sans-serif",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          fontFamily: "'Sora', sans-serif",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiInputBase-root": {
            fontFamily: "'Sora', sans-serif",
          },
          "& .MuiInputLabel-root": {
            fontFamily: "'Sora', sans-serif",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          fontFamily: "'Sora', sans-serif",
        },
      },
    },
  },
});

const App = () => {
  const [text, setText] = useState("");
  const [emotion, setEmotion] = useState("");
  const [songs, setSongs] = useState([]);
  const [details, setDetails] = useState("");
  const [loading, setLoading] = useState(false);
  const [webcamActive, setWebcamActive] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const webcamRef = useRef(null);

  // Use the Render backend URL
  const API_BASE_URL = "https://spotify-emoter.onrender.com";

  const analyzeText = async () => {
    setLoading(true);
    setEmotion("");
    setSongs([]);
    setDetails("");
    try {
      const res = await axios.post(`${API_BASE_URL}/text-emotion`, { text });
      setEmotion(res.data.emotion);
      setSongs(res.data.songs || []);
      setDetails(res.data.details);
    } catch (error) {
      console.error("Text analysis error:", error.response?.data || error);
      setEmotion("neutral");
      setSongs([]);
      setDetails("Error occurred while analyzing text");
    }
    setLoading(false);
  };

  const analyzeFace = async () => {
    setLoading(true);
    setEmotion("");
    setSongs([]);
    setDetails("");
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      setLoading(false);
      setDetails("Failed to capture image from webcam");
      return;
    }
    try {
      const res = await axios.post(`${API_BASE_URL}/face-emotion`, { image: imageSrc });
      setEmotion(res.data.emotion);
      setSongs(res.data.songs || []);
      setDetails(res.data.details);
    } catch (error) {
      console.error("Face analysis error:", error.response?.data || error);
      setEmotion("neutral");
      setSongs([]);
      setDetails("Error occurred while analyzing face");
    }
    setLoading(false);
    setWebcamActive(false);
  };

  useEffect(() => {
    let timeout;
    if (webcamActive) {
      setLoading(true);
      timeout = setTimeout(() => {
        analyzeFace();
      }, 5000);
    }
    return () => clearTimeout(timeout);
  }, [webcamActive]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <ThemeProvider theme={theme}>
      <Box className={`app-wrapper ${darkMode ? "dark" : "light"}`}>
        {/* Sidebar */}
        <motion.div
          className="sidebar"
          initial={{ x: -250 }}
          animate={{ x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box className="sidebar-content">
            <img
              src="https://storage.googleapis.com/pr-newsroom-wp/1/2023/05/Spotify_Primary_Logo_RGB_Green.png"
              alt="Spotify Logo"
              className="sidebar-logo"
            />
            <Typography variant="h5" className="sidebar-title">
              Feelin' Flow
            </Typography>
            <Box className="sidebar-nav">
              <Typography variant="body2" className="nav-item active">
                Home
              </Typography>
              <Box sx={{ mt: 2 }}>
                <IconButton color="inherit" onClick={toggleDarkMode} size="small">
                  {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
                </IconButton>
                <Switch
                  checked={darkMode}
                  onChange={toggleDarkMode}
                  color="default"
                  size="small"
                />
              </Box>
            </Box>
          </Box>
        </motion.div>

        {/* Main Content */}
        <Box className="main-content">
          <Container maxWidth="lg" sx={{ mt: 10, p: 3 }}>
            {/* Input Section */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              <Typography
                variant="h2"
                align="center"
                gutterBottom
                className="main-title"
                sx={{ fontWeight: 700 }}
              >
                Feelin’ Flow
              </Typography>
              <Grid container spacing={3} justifyContent="center">
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="How are you feeling?"
                    variant="outlined"
                    fullWidth
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="input-field"
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={analyzeText}
                    disabled={loading || !text}
                    fullWidth
                    sx={{ mt: 2 }}
                    className="action-button"
                  >
                    {loading ? <CircularProgress size={24} /> : "Analyze Text"}
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => setWebcamActive(!webcamActive)}
                    disabled={loading}
                    fullWidth
                    sx={{ mb: 2 }}
                    className="action-button"
                  >
                    {webcamActive ? "Analyzing... (5s)" : "Scan Face"}
                  </Button>
                  {webcamActive && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.5 }}
                    >
                      <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        width="100%"
                        className="webcam"
                      />
                    </motion.div>
                  )}
                </Grid>
              </Grid>
            </motion.div>

            {/* Loading State */}
            {loading && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="loading-container"
              >
                <CircularProgress />
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Detecting your emotion...
                </Typography>
              </motion.div>
            )}

            {/* Emotion Result */}
            {emotion && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="emotion-card"
              >
                <Card>
                  <CardMedia
                    component="img"
                    height="200"
                    image={songs[0]?.album_image || "https://via.placeholder.com/300x200"}
                    alt="Emotion Playlist"
                    className="emotion-image"
                  />
                  <CardContent>
                    <Typography variant="h4" className="emotion-title">
                      {emotion.toUpperCase()} PLAYLIST
                    </Typography>
                    <Typography variant="body1" className="emotion-details">
                      {details || "Curated based on your mood."}
                    </Typography>
                    <Typography variant="body2" className="emotion-stats">
                      ♥ {songs.length} Songs • {Math.floor(Math.random() * 1000)} Likes
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Song Recommendations */}
            {songs.length > 0 && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Typography variant="h5" align="center" sx={{ mt: 4, mb: 2 }}>
                  Your Feed
                </Typography>
                <Grid container spacing={2}>
                  {songs.map((song, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <motion.div
                        whileHover={{ scale: 1.05, boxShadow: "0 8px 20px rgba(0,0,0,0.2)" }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                      >
                        <Card className="song-card">
                          {song.album_image && (
                            <CardMedia
                              component="img"
                              height="140"
                              image={song.album_image}
                              alt={`${song.name} album cover`}
                              className="song-image"
                            />
                          )}
                          <CardContent>
                            <Typography variant="subtitle1" className="song-title">
                              <a href={song.url} target="_blank" rel="noopener noreferrer">
                                {song.name}
                              </a>
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {song.artist}
                            </Typography>
                            {song.artist_image && (
                              <img
                                src={song.artist_image}
                                alt={`${song.artist} image`}
                                className="artist-image"
                              />
                            )}
                            <Typography variant="caption" className="song-date">
                              {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                            </Typography>
                          </CardContent>
                        </Card>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </motion.div>
            )}

            {songs.length === 0 && emotion && !loading && (
              <Typography variant="h6" align="center" sx={{ mt: 4, color: "orange" }}>
                No songs found for this emotion.
              </Typography>
            )}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;