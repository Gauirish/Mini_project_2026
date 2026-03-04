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

  // Sorting by release date (recent first)
  filtered.sort((a, b) => {
    if (!a.release_date) return 1;
    if (!b.release_date) return -1;
    return new Date(b.release_date) - new Date(a.release_date);
  });

  return filtered;
}
