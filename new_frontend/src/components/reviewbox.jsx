import { useState } from "react";

function Reviewbox({ onAnalyze }) {
  const [reviewText, setReviewText] = useState("");

  const wordCount =
    reviewText.trim() === ""
      ? 0
      : reviewText.trim().split(/\s+/).length;

  const handleAnalyze = () => {
    const text = reviewText.trim();
    if (!text) return;

    // 1. Clear state IMMEDIATELY
    setReviewText("");

    // 2. Call parent handler
    onAnalyze(text);
  };

  return (
    <div style={{ marginTop: "30px" }}>
      <textarea
        value={reviewText}
        onChange={(e) => setReviewText(e.target.value)}
        placeholder="Write your review here..."
        style={{
          width: "100%",
          minHeight: "120px",
          padding: "16px",
          marginTop: "10px",
          resize: "vertical",
          borderRadius: "12px",
          background: "rgba(255,255,255,0.9)",
          border: "1px solid rgba(0, 0, 0, 0.1)", // Subtle border
          color: "#0f172a",
          fontSize: "15px",
          outline: "none",
          transition: "border-color 0.3s ease"
        }}
        onFocus={(e) => e.target.style.borderColor = "#3b82f6"}
        onBlur={(e) => e.target.style.borderColor = "rgba(0, 0, 0, 0.1)"}
      />

      <div style={{ marginTop: "12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: "12px", color: "#64748b" }}>
          Word Count: {wordCount}
        </div>

        <button
          onClick={handleAnalyze}
          className="save-btn-full"
          style={{ width: "auto", padding: "10px 24px" }}
        >
          Submit Your Review
        </button>
      </div>
    </div>
  );
}

export default Reviewbox;
