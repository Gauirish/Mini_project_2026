import { useState, useMemo, useEffect } from "react";
import { filterMovies } from "./utils/filtermovies";
import { paginate } from "./utils/paginate";
import Header from "./components/Header";
import Filterchips from "./components/Filterchips";
import Pagination from "./components/Pagination";
import Moviecard from "./components/Moviecard";
import Moviedetail from "./components/moviedetail";

function App() {
  const [moviesData, setMoviesData] = useState([]);
  const [selectedYear, setSelectedYear] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  const moviesPerPage = 16;

  // 🌗 Apply theme to body
  useEffect(() => {
    document.body.className = darkMode ? "dark-mode" : "light-mode";
  }, [darkMode]);

  // Fetch movies
  useEffect(() => {
    fetch("http://127.0.0.1:8000/movies")
      .then((res) => res.json())
      .then((data) => setMoviesData(data))
      .catch((err) => console.error("Error fetching movies:", err));
  }, []);

  // Generate years dynamically
  const years = useMemo(() => {
    const extractedYears = moviesData
      .map((movie) =>
        movie.release_date
          ? new Date(movie.release_date).getFullYear()
          : null
      )
      .filter(Boolean);

    const uniqueYears = [...new Set(extractedYears)].sort(
      (a, b) => b - a
    );

    return ["All", ...uniqueYears];
  }, [moviesData]);

  // Filtering
  const filteredMovies = useMemo(() => {
    return filterMovies(moviesData, selectedYear, searchQuery);
  }, [moviesData, selectedYear, searchQuery]);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedYear, searchQuery]);

  // Pagination
  const { currentMovies, totalPages } = useMemo(() => {
    return paginate(filteredMovies, currentPage, moviesPerPage);
  }, [filteredMovies, currentPage]);

  return (
    <div className="app-container">
      {selectedMovie ? (
        <Moviedetail
          movie={selectedMovie}
          onBack={() => setSelectedMovie(null)}
        />
      ) : (
        <>
          <div className="top-section">
            <Header
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              darkMode={darkMode}
              setDarkMode={setDarkMode}
            />

            <Filterchips
              years={years}
              selectedYear={selectedYear}
              setSelectedYear={setSelectedYear}
            />
          </div>

          <div className="movie-grid">
            {currentMovies.length > 0 ? (
              currentMovies.map((movie) => (
                <Moviecard
                  key={movie.id}
                  movie={movie}
                  onSelect={setSelectedMovie}
                />
              ))
            ) : (
              <p>No movies to display.</p>
            )}
          </div>

          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            setCurrentPage={setCurrentPage}
          />
        </>
      )}
    </div>
  );
}

export default App;