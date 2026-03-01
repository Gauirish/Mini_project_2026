import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import Moviedetail from "../components/moviedetail";

function MovieDetailsPage() {
    const { id } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const [movie, setMovie] = useState(location.state?.movie || null);
    const [loading, setLoading] = useState(!movie);

    useEffect(() => {
        if (!movie) {
            setLoading(true);
            fetch(`http://127.0.0.1:8000/movies/${id}`)
                .then((res) => res.json())
                .then((data) => {
                    setMovie(data);
                    setLoading(false);
                })
                .catch((err) => {
                    console.error("Error fetching movie details:", err);
                    setLoading(false);
                });
        }
    }, [id, movie]);

    if (loading) {
        return <div style={{ color: "white", padding: "20px" }}>Loading movie details...</div>;
    }

    if (!movie) {
        return (
            <div style={{ color: "white", padding: "20px" }}>
                <p>Movie not found.</p>
                <button onClick={() => navigate("/")}>Go Home</button>
            </div>
        );
    }

    return (
        <Moviedetail
            movie={movie}
            onBack={() => navigate("/")}
        />
    );
}

export default MovieDetailsPage;
