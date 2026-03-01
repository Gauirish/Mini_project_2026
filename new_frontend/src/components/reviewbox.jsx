import { useState } from "react";

function Reviewbox({ onAnalyze }) {
  const [reviewText, setReviewText] = useState("");

  const wordCount =
    reviewText.trim() === ""
      ? 0
      : reviewText.trim().split(/\s+/).length;

  const handleAnalyze = () => {
    if (reviewText.trim() === "") return;
    onAnalyze(reviewText);
  };

  return (
    <div style={{ marginTop: "30px" }}>
      <h3>Write Your Review</h3>

      <textarea
        value={reviewText}
        onChange={(e) => setReviewText(e.target.value)}
        placeholder="Write your review here..."
        style={{
          width: "100%",
          minHeight: "120px",
          padding: "12px",
          marginTop: "10px",
          resize: "vertical"
        }}
      />

      <div style={{ marginTop: "8px", fontSize: "12px" }}>
        Word Count: {wordCount}
      </div>

      <button
        onClick={handleAnalyze}
        style={{
          marginTop: "12px",
          padding: "8px 16px",
          cursor: "pointer"
        }}
      >
        Analyze with AI
      </button>
    </div>
  );
}

export default Reviewbox;
