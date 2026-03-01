function Moviecard({ movie, onSelect }) {
  const posterUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;

  return (
    <div
      onClick={() => onSelect(movie)}
      className="movie-card"
      style={{ cursor: "pointer" }}
    >
      <div className="poster-wrapper">
        {posterUrl ? (
          <img
            src={posterUrl}
            alt={movie.title}
            className="poster-image"
          />
        ) : (
          <div
            className="poster-placeholder"
            style={{
              width: "200px",
              height: "300px",
              background: "linear-gradient(135deg, #2c2c2c, #1a1a1a)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "12px",
              color: "#aaa",
              fontSize: "14px",
              textAlign: "center",
              padding: "10px"
            }}
          >
            No Poster Available
          </div>
        )}
      </div>

      <div className="movie-info">
        <h3 className="movie-title">{movie.title}</h3>
        <p className="movie-date">{movie.release_date}</p>
      </div>
    </div>
  );
}

export default Moviecard;