function Header({ searchQuery, setSearchQuery }) {
  return (
    <div style={{ marginBottom: "25px" }}>
      <h1 className="brand-title">
        CineSense Malayalam
      </h1>

      <div className="search-wrapper">
        <span className="search-icon">🔍</span>

        <input
          type="text"
          placeholder="Search Malayalam movies..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>
    </div>
  );
}

export default Header;
