export function paginate(movies, currentPage, moviesPerPage) {
  const totalMovies = movies.length;

  const totalPages =
    totalMovies === 0
      ? 0
      : Math.ceil(totalMovies / moviesPerPage);

  const startIndex = (currentPage - 1) * moviesPerPage;
  const endIndex = startIndex + moviesPerPage;

  const currentMovies = movies.slice(startIndex, endIndex);

  return { currentMovies, totalPages };
}