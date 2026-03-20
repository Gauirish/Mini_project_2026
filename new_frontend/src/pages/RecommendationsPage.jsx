import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { supabase } from "../supabaseClient";
import Moviecard from "../components/Moviecard";

function RecommendationsPage({ session }) {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState("");
    const navigate = useNavigate();
    const location = useLocation();
    const user = session?.user;

    useEffect(() => {
        if (!user) return;

        setLoading(true);
        fetch(`http://127.0.0.1:8000/recommendations/${user.id}?t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                if (data.movies && data.movies.length === 0) {
                    setMessage(data.message || "No recommendations found");
                    setMovies([]);
                } else if (Array.isArray(data)) {
                    setMovies(data);
                    setMessage("");
                } else if (data.message || data.error) {
                    setMessage(data.message || data.error);
                    setMovies([]);
                } else {
                    setMovies([]);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching recommendations:", err);
                setLoading(false);
            });
    }, [user, location.key]);

    const handleLogout = async () => {
        if (supabase) {
            await supabase.auth.signOut();
            navigate("/");
        }
    };

    const handleMovieSelect = (movie) => {
        // Recommendations from TMDB might not be in our DB yet
        // Moviecard expects an id, for recommendations we can pass tmdb_id
        navigate(`/movie/${movie.id}`, { state: { movie } });
    };

    return (
        <div className="dashboard-container">
            {/* Left Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-profile" onClick={() => navigate("/profile")}>
                    <div className="sidebar-avatar">
                        {(user?.user_metadata?.full_name || user?.email?.split('@')[0] || "U").charAt(0).toUpperCase()}
                    </div>
                    <span className="welcome-text">
                        Welcome, {user?.user_metadata?.full_name || user?.email?.split('@')[0]?.split('.')[0]}
                    </span>
                </div>

                <div className="glow-line"></div>

                <nav className="sidebar-nav">
                    <button className="nav-button" onClick={() => navigate("/")}>
                        <span>🏠</span> Home
                    </button>
                    <button className="nav-button" onClick={() => navigate("/your-reviews")}>
                        <span>📝</span> Your Reviews
                    </button>
                    <button className="nav-button active" onClick={() => navigate("/recommendations")}>
                        <span>✨</span> Recommended for You
                    </button>
                    <button className="nav-button" onClick={handleLogout} style={{ marginTop: 'auto', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
                        <span>🚪</span> Logout
                    </button>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <div className="top-section">
                    <h1 className="brand-title">Picked Just For You</h1>
                    <p style={{ color: "#0f172a", textAlign: 'center' }}>
                        Based on your cinematic taste and review history
                    </p>
                </div>

                {
                    loading ? (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p className="loading-text">According to your reviews, you would like to watch :)</p>
                        </div>
                    ) : (movies.length === 0) ? (
                        <div className="no-reviews-empty">
                            <h2>{message || "No recommendations found"}</h2>
                            <p>Try reviewing some more movies to help our AI understand your taste better!</p>
                            <button onClick={() => navigate("/")} className="auth-button" style={{ width: 'auto', marginTop: '20px' }}>
                                Start Reviewing
                            </button>
                        </div>
                    ) : (
                        <div className="recommendations-container">
                            <div className="movie-grid">
                                {movies.map((movie) => (
                                    <div key={movie.id} className="recommendation-item">
                                        <Moviecard
                                            movie={movie}
                                            onClick={() => handleMovieSelect(movie)}
                                        />
                                        {movie.ai_reason && (
                                            <div className="ai-badge-tooltip">
                                                ✨ {movie.ai_reason}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )
                }
            </main >
        </div >
    );
}

export default RecommendationsPage;
