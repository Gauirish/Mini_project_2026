function Header({ searchQuery, setSearchQuery }) {
  return (
    <div style={{ marginBottom: "25px", textAlign: "center" }}>
      <h1 className="brand-title">
        CINE — SENSE
      </h1>

      <div className="search-wrapper">
        {/* Professional SVG Icon */}
        <svg
          className="search-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth="2"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-4.35-4.35m1.85-5.65a7.5 7.5 0 11-15 0 7.5 7.5 0 0115 0z"
          />
        </svg>

        <input
          type="text"
          placeholder="Search movies"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>
    </div>
  );
}

export default Header;