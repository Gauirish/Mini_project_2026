import { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { filterMovies } from "../utils/filtermovies";
import { paginate } from "../utils/paginate";
import Header from "../components/Header";
import Filterchips from "../components/Filterchips";
import Pagination from "../components/Pagination";
import Moviecard from "../components/Moviecard";

function Home({ session, handleLogout }) {
    const [moviesData, setMoviesData] = useState([]);
    const [selectedYear, setSelectedYear] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [darkMode, setDarkMode] = useState(true);
    const navigate = useNavigate();

    const moviesPerPage = 20;
    const years = ["All", 2026, 2025, 2024];

    // ✅ Fetch movies from backend
    useEffect(() => {
        setIsLoading(true);
        fetch("http://127.0.0.1:8000/movies")
            .then((res) => res.json())
            .then((data) => {
                setMoviesData(data);
                setIsLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching movies:", err);
                setIsLoading(false);
            });
    }, []);

    // Apply filtering
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

    const handleMovieSelect = (movie) => {
        navigate(`/movie/${movie.id}`, { state: { movie } });
    };

    return (
        <div className="dashboard-container">
            {/* Left Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-profile" onClick={() => navigate("/profile")}>
                    <div className="sidebar-avatar">
                        {(session?.user?.user_metadata?.full_name || session?.user?.email?.split('@')[0] || "U").charAt(0).toUpperCase()}
                    </div>
                    <span className="welcome-text">
                        Welcome, {session?.user?.user_metadata?.full_name || session?.user?.email?.split('@')[0]?.split('.')[0]}
                    </span>
                </div>

                <div className="glow-line"></div>

                <nav className="sidebar-nav">
                    <button className="nav-button active" onClick={() => navigate("/")}>
                        <span>🏠</span> Home
                    </button>
                    <button className="nav-button" onClick={() => navigate("/your-reviews")}>
                        <span>📝</span> Your Reviews
                    </button>
                    <button className="nav-button" onClick={() => navigate("/recommendations")}>
                        <span>✨</span> Recommended for You
                    </button>
                    <button className="nav-button" onClick={handleLogout} style={{ marginTop: 'auto', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
                        <span>🚪</span> Logout
                    </button>
                </nav>
            </aside>

            {/* Main Content Area */}
            <main className="main-content">
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

                {isLoading ? (
                    <div className="loading-container">
                        <div className="spinner"></div>
                        <p className="loading-text">Bringing you the best movies...</p>
                    </div>
                ) : (
                    <>
                        <div className="movie-grid">
                            {currentMovies && currentMovies.length > 0 ? (
                                currentMovies.map((movie) => (
                                    <Moviecard
                                        key={movie.id}
                                        movie={movie}
                                        onSelect={handleMovieSelect}
                                    />
                                ))
                            ) : (
                                <p style={{ color: "white", padding: "20px" }}>No movies to display.</p>
                            )}
                        </div>

                        <Pagination
                            currentPage={currentPage}
                            totalPages={totalPages}
                            setCurrentPage={setCurrentPage}
                        />
                    </>
                )}
            </main>
        </div>
    );
}

export default Home;
