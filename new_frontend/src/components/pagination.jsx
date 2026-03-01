function Pagination({ currentPage, totalPages, setCurrentPage }) {
  if (totalPages === 0) return null;

  return (
    <div style={{ marginTop: "30px" }}>
      <button
        onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
        disabled={currentPage === 1}
      >
        ← Previous
      </button>

      <span style={{ margin: "0 15px" }}>
        Page {currentPage} of {totalPages}
      </span>

      <button
        onClick={() =>
          setCurrentPage((prev) =>
            prev < totalPages ? prev + 1 : prev
          )
        }
        disabled={currentPage === totalPages}
      >
        Next →
      </button>
    </div>
  );
}

export default Pagination;