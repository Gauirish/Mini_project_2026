import { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { filterMovies } from "../utils/filtermovies";
import { paginate } from "../utils/paginate";
import Header from "../components/Header";
import Filterchips from "../components/Filterchips";
import Pagination from "../components/Pagination";
import Moviecard from "../components/Moviecard";

function Home() {
    const [moviesData, setMoviesData] = useState([]);
    const [selectedYear, setSelectedYear] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    const moviesPerPage = 16;

    // ✅ Fetch movies from backend
    useEffect(() => {
        setIsLoading(true);
        fetch("http://127.0.0.1:8000/movies")
            .then((res) => res.json())
            .then((data) => {
                console.log("MOVIES FROM BACKEND:", data);
                setMoviesData(data);
                setIsLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching movies:", err);
                setIsLoading(false);
            });
    }, []);

    // ✅ Apply filtering
    const filteredMovies = useMemo(() => {
        return filterMovies(moviesData, selectedYear, searchQuery);
    }, [moviesData, selectedYear, searchQuery]);

    // Reset page when filter/search changes
    useEffect(() => {
        setCurrentPage(1);
    }, [selectedYear, searchQuery]);

    // ✅ Apply pagination
    const { currentMovies, totalPages } = useMemo(() => {
        return paginate(filteredMovies, currentPage, moviesPerPage);
    }, [filteredMovies, currentPage]);

    const handleMovieSelect = (movie) => {
        navigate(`/movie/${movie.id}`, { state: { movie } });
    };

    return (
        <>
            <div className="top-section">
                <Header
                    searchQuery={searchQuery}
                    setSearchQuery={setSearchQuery}
                />

                <Filterchips
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
                    <div
                        style={{
                            display: "flex",
                            flexWrap: "wrap",
                            gap: "20px",
                            marginTop: "20px"
                        }}
                    >
                        {currentMovies && currentMovies.length > 0 ? (
                            currentMovies.map((movie) => (
                                <Moviecard
                                    key={movie.id}
                                    movie={movie}
                                    onSelect={handleMovieSelect}
                                />
                            ))
                        ) : (
                            <p style={{ color: "white" }}>No movies to display.</p>
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
    );
}

export default Home;
