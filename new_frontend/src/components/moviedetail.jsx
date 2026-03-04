import Reviewbox from "./Reviewbox.jsx";
import StarRating from "./StarRating";
import { useState, useEffect } from "react";

function Moviedetail({ movie, onBack }) {
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [aspectAverages, setAspectAverages] = useState(null);
  const [aspectsLoading, setAspectsLoading] = useState(true);

  const [highlightReviews, setHighlightReviews] = useState({
    positive: null,
    negative: null
  });

  const posterUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;

  // Fetch aspect averages
  useEffect(() => {
    setAspectsLoading(true);

    fetch(`https://miniproject2026-production.up.railway.app/movie-aspects/${movie.id}`)
      .then((res) => res.json())
      .then((data) => {
        setAspectAverages(data);
        setAspectsLoading(false);
      })
      .catch(() => setAspectsLoading(false));
  }, [movie.id]);

  // Fetch highlight reviews
  useEffect(() => {
    fetch(`https://miniproject2026-production.up.railway.app/movie-highlights/${movie.id}`)
      .then((res) => res.json())
      .then((data) => setHighlightReviews(data))
      .catch((err) => console.error(err));
  }, [movie.id]);

  const handleAnalyze = async (text) => {
    if (!text) return;

    setLoading(true);

    try {
      const response = await fetch("https://miniproject2026-production.up.railway.app/analyze-review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_id: movie.id,
          review: text
        })
      });

      const data = await response.json();
      setAnalysisResult(data);

      // Refresh aspects after new review
      const refresh = await fetch(
        `https://miniproject2026-production.up.railway.app/movie-aspects/${movie.id}`
      );
      const updated = await refresh.json();
      setAspectAverages(updated);

    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  const getAspectColor = (value) => {
    if (value >= 4)
      return { border: "#22c55e", bg: "rgba(34,197,94,0.15)", text: "#22c55e" };
    if (value >= 3)
      return { border: "#facc15", bg: "rgba(250,204,21,0.15)", text: "#facc15" };
    if (value > 0)
      return { border: "#ef4444", bg: "rgba(239,68,68,0.15)", text: "#ef4444" };

    return { border: "#374151", bg: "#1f2937", text: "#9ca3af" };
  };

  return (
    <div style={{ padding: "20px" }}>
      <button onClick={onBack} style={{ marginBottom: "20px" }}>
        ← Back
      </button>

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

          {/* Aspect Bubbles */}
          <div style={{ marginTop: "18px", display: "flex", flexWrap: "wrap", gap: "10px" }}>
            {aspectsLoading ? (
              <span style={{ color: "#9ca3af" }}>Loading aspects...</span>
            ) : (
              aspectAverages &&
              Object.entries(aspectAverages).map(([key, value]) => {
                const colors = getAspectColor(value);
                return (
                  <div
                    key={key}
                    style={{
                      padding: "6px 14px",
                      borderRadius: "20px",
                      border: `1px solid ${colors.border}`,
                      backgroundColor: colors.bg,
                      color: colors.text,
                      fontWeight: "600",
                      fontSize: "14px"
                    }}
                  >
                    {key.toUpperCase()}: {value}
                  </div>
                );
              })
            )}
          </div>

          {/* Highlight Reviews (Clean + Professional) */}
          <div style={{ marginTop: "20px", maxWidth: "600px" }}>
            {highlightReviews.positive && (
              <div
                style={{
                  marginBottom: "12px",
                  padding: "14px",
                  borderLeft: "4px solid #22c55e",
                  background: "rgba(34,197,94,0.08)",
                  borderRadius: "8px",
                  lineHeight: "1.5",
                  fontSize: "14px",
                  display: "-webkit-box",
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden"
                }}
              >
                {highlightReviews.positive}
              </div>
            )}

            {highlightReviews.negative && (
              <div
                style={{
                  padding: "14px",
                  borderLeft: "4px solid #ef4444",
                  background: "rgba(239,68,68,0.08)",
                  borderRadius: "8px",
                  lineHeight: "1.5",
                  fontSize: "14px",
                  display: "-webkit-box",
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden"
                }}
              >
                {highlightReviews.negative}
              </div>
            )}
          </div>
        </div>
      </div>

      <Reviewbox onAnalyze={handleAnalyze} />

      {loading && <p>Analyzing with AI...</p>}

      {analysisResult && (
        <div style={{ marginTop: "20px" }}>
          <h3>Latest AI Rating</h3>
          <StarRating rating={analysisResult.rating} size={22} />
          <p>Sentiment: {analysisResult.sentiment}</p>
        </div>
      )}
    </div>
  );
}

export default Moviedetail;