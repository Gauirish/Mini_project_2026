import Reviewbox from "./reviewbox";
import { useState } from "react";
import Analysisresult from "./analysisresult";


function Moviedetail({ movie, onBack }) {
    const [loading, setLoading] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);

  const posterUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;

  return (
    <div style={{ padding: "20px" }}>
      <button
        onClick={onBack}
        style={{
          marginBottom: "20px",
          padding: "6px 12px",
          cursor: "pointer"
        }}
      >
        ← Back
      </button>

      <div style={{ display: "flex", gap: "30px" }}>
        {posterUrl ? (
          <img
            src={posterUrl}
            alt={movie.title}
            style={{ width: "300px", borderRadius: "8px" }}
          />
        ) : (
          <div
            style={{
              width: "300px",
              height: "450px",
              backgroundColor: "#ddd",
              borderRadius: "8px"
            }}
          />
        )}

        <div>
          <h2>{movie.title}</h2>
          <p><strong>Release Date:</strong> {movie.release_date}</p>
          <p style={{ marginTop: "10px", maxWidth: "600px" }}>
            {movie.overview || "No overview available."}
          </p>
        </div>
      </div>

     <Reviewbox
  onAnalyze={(text) => {
    setLoading(true);
    setAnalysisResult(null);

    setTimeout(() => {
      const fakeRating = Math.floor(Math.random() * 5) + 1;

      let sentiment = "Neutral";
      if (fakeRating >= 4) sentiment = "Positive";
      if (fakeRating <= 2) sentiment = "Negative";

      setAnalysisResult({
        rating: fakeRating,
        sentiment: sentiment,
        confidence: (Math.random() * 20 + 80).toFixed(2)
      });

      setLoading(false);
    }, 1500);
  }}
/>

    </div>
  );
}

export default Moviedetail;
