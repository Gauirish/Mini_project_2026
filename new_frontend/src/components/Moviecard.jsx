import React from "react";

function Moviecard({ movie, onSelect }) {
  const posterUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;

  const numericRating = movie.avg_rating
    ? parseFloat(movie.avg_rating)
    : 0;

  const rating = numericRating.toFixed(1);

  const percentage = (numericRating / 5) * 100;

  const getColor = () => {
    if (numericRating >= 4) return "#22c55e"; // Green
    if (numericRating >= 3) return "#facc15"; // Yellow
    return "#ef4444"; // Red
  };

  const color = getColor();

  return (
    <div
      onClick={() => onSelect(movie)}
      className="movie-card"
      style={{
        cursor: "pointer",
        width: "220px"
      }}
    >
      <div className="poster-container">
        {posterUrl ? (
          <img
            src={posterUrl}
            alt={movie.title}
            className="poster-image"
          />
        ) : (
          <div className="no-poster">
            No Poster Available
          </div>
        )}

        {/* ⭐ Circular Progress Rating */}
        <div
          className="rating-wrapper"
          style={{
            background: `conic-gradient(${color} ${percentage}%, rgba(255,255,255,0.15) ${percentage}%)`
          }}
        >
          <div className="rating-inner">
            {rating}
          </div>
        </div>

        {/* Glossy Overlay */}
        <div className="gloss-overlay"></div>
      </div>

      <div style={{ marginTop: "10px" }}>
        <h4 style={{ margin: "0", fontSize: "14px" }}>
          {movie.title}
        </h4>
        <p style={{ fontSize: "12px", opacity: 0.7 }}>
          {movie.release_date}
        </p>
      </div>

      <style>{`
        .poster-container {
          position: relative;
          overflow: hidden;
          border-radius: 14px;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .poster-image {
          width: 100%;
          display: block;
          transition: transform 0.4s ease;
        }

        .no-poster {
          width: 100%;
          height: 330px;
          background-color: #333;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        /* Hover Effects */
        .movie-card:hover .poster-container {
          transform: translateY(-6px);
          box-shadow: 0 15px 30px rgba(0, 0, 0, 0.6);
        }

        .movie-card:hover .poster-image {
          transform: scale(1.1);
        }

        /* Progress Ring Wrapper */
        .rating-wrapper {
          position: absolute;
          bottom: 12px;
          right: 12px;
          width: 55px;
          height: 55px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 0 15px rgba(0,0,0,0.6);
          transition: transform 0.3s ease;
        }

        .movie-card:hover .rating-wrapper {
          transform: scale(1.1);
        }

        /* Inner Circle */
        .rating-inner {
          width: 42px;
          height: 42px;
          border-radius: 50%;
          background: radial-gradient(circle at 30% 30%, #1f2937, #111827);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: white;
          font-size: 14px;
        }

        /* Gloss Sweep */
        .gloss-overlay {
          position: absolute;
          top: 0;
          left: -75%;
          width: 50%;
          height: 100%;
          background: linear-gradient(
            120deg,
            rgba(255, 255, 255, 0.15) 0%,
            rgba(255, 255, 255, 0.3) 50%,
            rgba(255, 255, 255, 0.15) 100%
          );
          transform: skewX(-25deg);
          transition: left 0.6s ease;
        }

        .movie-card:hover .gloss-overlay {
          left: 130%;
        }
      `}</style>
    </div>
  );
}

export default Moviecard;