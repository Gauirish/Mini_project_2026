function Analysisresult({ result, loading }) {
  if (loading) {
    return (
      <div style={{ marginTop: "20px" }}>
        <p>Analyzing review...</p>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div style={{ marginTop: "20px", padding: "15px", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h4>AI Analysis Result</h4>
      <p><strong>Rating:</strong> {result.rating} / 5 ⭐</p>
      <p><strong>Sentiment:</strong> {result.sentiment}</p>
      <p><strong>Confidence:</strong> {result.confidence}%</p>
    </div>
  );
}

export default Analysisresult;
