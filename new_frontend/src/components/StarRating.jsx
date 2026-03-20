function StarRating({ rating, size = 22 }) {
  const fullStars = Math.floor(rating);
  const decimal = rating - fullStars;

  const stars = [];

  for (let i = 0; i < 5; i++) {
    if (i < fullStars) {
      stars.push(
        <span key={i} style={{ color: "#facc15", fontSize: size }}>
          ★
        </span>
      );
    } else if (i === fullStars && decimal > 0) {
      stars.push(
        <span
          key={i}
          style={{
            position: "relative",
            display: "inline-block",
            fontSize: size,
            color: "#94a3b8"
          }}
        >
          ★
          <span
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: `${decimal * 100}%`,
              overflow: "hidden",
              color: "#facc15"
            }}
          >
            ★
          </span>
        </span>
      );
    } else {
      stars.push(
        <span key={i} style={{ color: "#94a3b8", fontSize: size }}>
          ★
        </span>
      );
    }
  }

  return <div style={{ display: "flex", gap: "3px" }}>{stars}</div>;
}

export default StarRating;