import Reviewbox from "./reviewbox";
import StarRating from "./StarRating";
import { useState, useEffect, useMemo } from "react";

function Moviedetail({ movie, onBack, session }) {
  const [loading, setLoading] = useState(false);
  const [allReviews, setAllReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [aspectAverages, setAspectAverages] = useState(null);
  const [aspectsLoading, setAspectsLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const user = session?.user;
  // Use metadata full_name or first_name, otherwise fallback to email
  const firstName = user?.user_metadata?.full_name || user?.user_metadata?.first_name || user?.email?.split('@')[0] || "User";

  const posterUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;

  // Initial fetch for reviews AND overall aspects
  useEffect(() => {
    setAllReviews([]);
    setOffset(0);
    setHasMore(true);
    fetchReviews(0, true);
    fetchAspects();
  }, [movie.id]);

  const fetchAspects = async () => {
    setAspectsLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/movie-aspects/${movie.id}`);
      const data = await res.json();
      setAspectAverages(data);
    } catch (err) {
      console.error(err);
    } finally {
      setAspectsLoading(false);
    }
  };

  const fetchReviews = async (currentOffset, isInitial = false) => {
    try {
      if (isInitial) setReviewsLoading(true);
      const limit = 5;
      const response = await fetch(`http://127.0.0.1:8000/movie-reviews/${movie.id}?limit=${limit}&offset=${currentOffset}`);
      const data = await response.json();

      if (isInitial) {
        setAllReviews(data);
      } else {
        setAllReviews(prev => [...prev, ...data]);
      }

      if (data.length < limit) {
        setHasMore(false);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setReviewsLoading(false);
    }
  };

  const loadMore = () => {
    const nextOffset = offset + 5;
    setOffset(nextOffset);
    fetchReviews(nextOffset);
  };

  // We no longer calculate averages locally; we fetch them from the backend

  // Handle Review Submission
  const handleAnalyze = async (text) => {
    if (!text) return;
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze-review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_id: movie.id,
          review: text,
          user_id: user?.id,
          user_name: firstName
        })
      });

      const data = await response.json();

      // Add to local state immediately for instant feedback
      const newReview = {
        id: data.review_id,
        text: text,
        rating: data.rating,
        sentiment: data.sentiment,
        aspects: data.aspects,
        user_name: firstName,
        created_at: new Date().toISOString()
      };

      setAllReviews(prev => [newReview, ...prev]);
      // Update offset if we added one locally
      setOffset(prev => prev + 1);

      // Refresh overall aspects
      fetchAspects();

      return true; // Indicate success for clearing input
    } catch (error) {
      console.error(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <div style={{ display: "flex", gap: "30px" }}>
        {posterUrl && (
          <img
            src={posterUrl}
            alt={movie.title}
            style={{ width: "300px", borderRadius: "8px" }}
          />
        )}

        <div>
          <h2>{movie.title}</h2>
          <p><strong>Release Date:</strong> {movie.release_date}</p>
          <p style={{ marginTop: "10px", maxWidth: "600px" }}>
            {movie.overview || "No overview available."}
          </p>

          {/* ⭐ Average Rating */}
          {movie.avg_rating !== null && (
            <div style={{ marginTop: "15px", display: "flex", gap: "12px", alignItems: "center" }}>
              <StarRating rating={parseFloat(movie.avg_rating)} size={24} />
              <span style={{ fontWeight: "600" }}>
                {parseFloat(movie.avg_rating).toFixed(1)}
              </span>
            </div>
          )}

          <div className="aspect-bars-grid">
            {aspectsLoading ? (
              <span style={{ color: "#9ca3af" }}>Loading overall analysis...</span>
            ) : (
              aspectAverages &&
              Object.entries(aspectAverages).map(([key, value]) => {
                const percentage = (value / 5) * 100;
                return (
                  <div key={key} className="aspect-bar-row">
                    <div className="aspect-bar-header">
                      <span className="aspect-bar-label">{key}</span>
                      <span className="aspect-bar-value">{value.toFixed(1)} / 5.0</span>
                    </div>
                    <div className="aspect-bar-container">
                      <div
                        className="aspect-bar-fill"
                        style={{
                          width: `${percentage}%`,
                          backgroundSize: `${(100 / percentage) * 100}% 100%` // This keeps the red->yellow->green gradient correctly scaled to the width
                        }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      <div style={{ marginTop: "40px", display: "flex", flexDirection: "column", gap: "40px" }}>
        {/* Review Input */}
        <div>
          <h3 style={{ marginBottom: "15px" }}>Write your review</h3>
          <Reviewbox onAnalyze={handleAnalyze} />
          {loading && <p style={{ color: "#3b82f6", marginTop: "10px" }}>Submitting your review...</p>}
        </div>

        {/* User Reviews List */}
        <div>
          <h3 style={{ marginBottom: "20px" }}>Recent Reviews</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {allReviews.map((rev) => (
              <div key={rev.id} className="user-review-card">
                <div className="review-user-info">
                  <div className="review-avatar">
                    {rev.user_name.charAt(0).toUpperCase()}
                  </div>
                  <span className="review-username">{rev.user_name}</span>
                </div>
                <div className="review-content">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <StarRating rating={rev.rating} size={16} />
                    <span style={{ fontSize: "12px", color: "#64748b" }}>
                      {new Date(rev.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="review-text-display">{rev.text}</p>
                </div>
              </div>
            ))}
            {allReviews.length === 0 && !reviewsLoading && (
              <p style={{ color: "#64748b", fontStyle: "italic" }}>No reviews yet. Be the first to analyze!</p>
            )}

            {hasMore && allReviews.length >= 5 && (
              <button
                onClick={loadMore}
                className="secondary-btn-full"
                style={{ marginTop: "10px", width: "auto", alignSelf: "center" }}
              >
                Load More Reviews
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Moviedetail;