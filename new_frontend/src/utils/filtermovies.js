export function filterMovies(movies, selectedYear, searchQuery) {
  let filtered = movies;

  if (selectedYear && selectedYear !== "All") {
    filtered = filtered.filter((movie) => {
      if (!movie.release_date) return false;
      return movie.release_date.startsWith(selectedYear);
    });
  }

  if (searchQuery.trim() !== "") {
    filtered = filtered.filter((movie) =>
      movie.title.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }

  return filtered;
}
