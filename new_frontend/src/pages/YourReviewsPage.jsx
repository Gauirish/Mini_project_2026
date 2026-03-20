import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../supabaseClient";

function YourReviewsPage({ session }) {
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const user = session?.user;

    useEffect(() => {
        if (!user) return;

        fetch(`http://127.0.0.1:8000/user-reviews/${user.id}`)
            .then(res => res.json())
            .then(data => {
                setReviews(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching user reviews:", err);
                setLoading(false);
            });
    }, [user]);

    const handleLogout = async () => {
        if (supabase) {
            await supabase.auth.signOut();
            navigate("/");
        }
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
                    <button className="nav-button active" onClick={() => navigate("/your-reviews")}>
                        <span>📝</span> Your Reviews
                    </button>
                    <button className="nav-button">
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
                    <h1 className="brand-title">Your Review History</h1>
                    <p style={{ color: "#0f172a", textAlign: 'center' }}>Total Analysis: {reviews.length}</p>
                </div>

                {loading ? (
                    <div className="loading-container">
                        <div className="spinner"></div>
                        <p className="loading-text">Fetching your cinematic history...</p>
                    </div>
                ) : reviews.length > 0 ? (
                    <div className="user-reviews-grid">
                        {reviews.map((review) => (
                            <div key={review.id} className="user-review-item-card">
                                <div className="review-poster-section">
                                    <img
                                        src={review.poster_path ? `https://image.tmdb.org/t/p/w500${review.poster_path}` : "/placeholder.jpg"}
                                        alt={review.movie_title}
                                        className="review-poster-mini"
                                        onClick={() => navigate(`/movie/${review.movie_id}`)}
                                        style={{ cursor: 'pointer' }}
                                    />
                                </div>
                                <div className="review-body-section">
                                    <div className="review-card-header">
                                        <div className="review-movie-info">
                                            <h3 className="review-movie-title" onClick={() => navigate(`/movie/${review.movie_id}`)} style={{ cursor: 'pointer' }}>
                                                {review.movie_title}
                                            </h3>
                                            <span className="review-rating-tag">⭐ {review.rating.toFixed(1)} / 5.0</span>
                                        </div>
                                        <span className="review-date-top">
                                            {new Date(review.created_at).toLocaleDateString(undefined, {
                                                year: 'numeric',
                                                month: 'short',
                                                day: 'numeric'
                                            })}
                                        </span>
                                    </div>
                                    <p className="review-text-content">"{review.text}"</p>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="no-reviews-empty">
                        <h2>No reviews yet</h2>
                        <p>Start analyzing movies to see your history here!</p>
                        <button onClick={() => navigate("/")} className="auth-button" style={{ width: 'auto', marginTop: '20px' }}>
                            Browse Movies
                        </button>
                    </div>
                )}
            </main>
        </div>
    );
}

export default YourReviewsPage;
