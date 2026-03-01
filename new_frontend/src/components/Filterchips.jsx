function Filterchips({ selectedYear, setSelectedYear }) {
  const years = ["All", "2025", "2024", "2023", "2022"];

  return (
    <div
  style={{
    marginTop: "10px",
    display: "flex",
    justifyContent: "center",
    flexWrap: "wrap"
  }}
>

      {years.map((year) => (
        <button
          key={year}
          onClick={() => setSelectedYear(year)}
          style={{
            marginRight: "8px",
            marginBottom: "8px",
            padding: "6px 14px",
            borderRadius: "0px",
            border: selectedYear === year
              ? "1px solid #3b82f6"
              : "1px solid #cbd5e1",
            backgroundColor: selectedYear === year
              ? "#3b82f6"
              : "#ffffff",
            color: selectedYear === year
              ? "#ffffff"
              : "#1e293b",
            fontSize: "14px",
            transition: "all 0.2s ease"
          }}
        >
          {year}
        </button>
      ))}
    </div>
  );
}

export default Filterchips;
