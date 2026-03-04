import { useState, useMemo, useEffect } from "react";
import { supabase } from "./supabaseClient";
import Auth from "./pages/Auth.jsx";
import { filterMovies } from "./utils/filtermovies";
import { paginate } from "./utils/paginate";
import Header from "./components/Header.jsx";
import Filterchips from "./components/Filterchips.jsx";
import Pagination from "./components/Pagination.jsx";
import Moviecard from "./components/Moviecard.jsx";
import Moviedetail from "./components/Moviedetail.jsx";

function App() {
  console.log("App Rendering - Supabase:", !!supabase);
  const [session, setSession] = useState(null);
  const [moviesData, setMoviesData] = useState([]);
  const [selectedYear, setSelectedYear] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  const moviesPerPage = 20;

  // 🔐 Check session on mount
  useEffect(() => {
    if (!supabase) return;

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  // 🌗 Apply theme to body
  useEffect(() => {
    document.body.className = darkMode ? "dark-mode" : "light-mode";
  }, [darkMode]);

  // Fetch movies
  useEffect(() => {
    if (!session) return;
    setIsLoading(true);
    fetch("https://miniproject2026-production.up.railway.app/movies")
      .then((res) => res.json())
      .then((data) => {
        setMoviesData(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching movies:", err);
        setIsLoading(false);
      });
  }, [session]);

  const handleLogout = async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
  };

  // Generate years dynamically
  const years = ["All", 2026, 2025, 2024];

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

  if (!supabase) {
    return (
      <div className="auth-wrapper">
        <div className="auth-container">
          <h1 className="brand-title">CineSense</h1>
          <h2 className="auth-title">Configuration Required</h2>
          <p className="auth-subtitle">
            Please update your <code>.env</code> file with your Supabase credentials to enable authentication and access the app.
          </p>
          <div className="auth-message error">
            Missing <code>VITE_SUPABASE_URL</code> or <code>VITE_SUPABASE_ANON_KEY</code>.
          </div>
        </div>
      </div>
    );
  }

  if (!session) {
    return <Auth />;
  }

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
            <div style={{ display: 'flex', justifyContent: 'flex-end', paddingBottom: '10px' }}>
              <button onClick={handleLogout} className="logout-button" style={{
                background: 'rgba(255,255,255,0.1)',
                color: 'white',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '13px'
              }}>
                Logout
              </button>
            </div>
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

          {isLoading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p className="loading-text">Bringing you the best movies...</p>
            </div>
          ) : (
            <>
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
        </>
      )}
    </div>
  );
}

export default App;