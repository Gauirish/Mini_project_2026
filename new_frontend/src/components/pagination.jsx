function Pagination({ currentPage, totalPages, setCurrentPage }) {
  if (totalPages === 0) return null;

  return (
    <div className="pagination-container">
      <button
        className="pagination-btn"
        onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
        disabled={currentPage === 1}
      >
        ← Previous
      </button>

      <span className="pagination-text">
        Page {currentPage} of {totalPages}
      </span>

      <button
        className="pagination-btn"
        onClick={() =>
          setCurrentPage((prev) =>
            prev < totalPages ? prev + 1 : prev
          )
        }
        disabled={currentPage === totalPages}
      >
        Next →
      </button>

      <style>{`
        .pagination-container {
          margin-top: 40px;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 25px;
        }

        .pagination-btn {
          padding: 8px 18px;
          border-radius: 8px;
          border: none;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.25s ease;
          background: linear-gradient(135deg, #22d3ee, #3b82f6);
          color: white;
          box-shadow: 0 0 10px rgba(34, 211, 238, 0.4);
        }

        .pagination-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 0 20px rgba(34, 211, 238, 0.7);
        }

        .pagination-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
          box-shadow: none;
        }

        .pagination-text {
          font-weight: 600;
          letter-spacing: 0.5px;
        }
      `}</style>
    </div>
  );
}

export default Pagination;