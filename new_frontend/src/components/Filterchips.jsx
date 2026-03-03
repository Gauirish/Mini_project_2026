function Filterchips({ years, selectedYear, setSelectedYear }) {
  return (
    <>
      <div className="filter-container">
        {years.map((year) => (
          <button
            key={year}
            onClick={() => setSelectedYear(year)}
            className={`filter-chip ${
              selectedYear === year ? "active-chip" : ""
            }`}
          >
            {year}
          </button>
        ))}
      </div>

      <style>{`
        .filter-container {
          margin-top: 18px;
          display: flex;
          justify-content: center;
          flex-wrap: wrap;
          gap: 14px;
        }

        .filter-chip {
          padding: 10px 22px;
          border-radius: 12px;
          border: none;
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          color: white;
          background: linear-gradient(135deg, #22d3ee, #3b82f6);
          transition: all 0.3s ease;
          box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
        }

        /* HOVER — SAME STYLE AS PAGINATION */
        .filter-chip:hover {
          transform: translateY(-3px);
          box-shadow:
            0 0 20px rgba(34, 211, 238, 1),
            0 0 35px rgba(59, 130, 246, 0.8);
        }

        /* ACTIVE CHIP — STRONGER GLOW */
        .active-chip {
          box-shadow:
            0 0 18px rgba(34, 211, 238, 1),
            0 0 35px rgba(59, 130, 246, 1),
            0 0 60px rgba(59, 130, 246, 0.9);
        }
      `}</style>
    </>
  );
}

export default Filterchips;