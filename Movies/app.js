const grid = document.getElementById("movie-grid");
const searchInput = document.getElementById("movie-search");

let allMovies = [];
let currentMovie = null;

// App startup: wire up events and load the movie list once.
initializePage();

// Initial page setup.
async function initializePage() {
  attachSearchListener();
  await loadMovies();
}

// Search input: redraw the grid as the user types.
function attachSearchListener() {
  searchInput.addEventListener("input", () => {
    displayMovies(getFilteredMovies(searchInput.value));
  });
}

// Data loading: fetch the scanned movie catalog from the server.
async function loadMovies() {
  const response = await fetch("/Movies/movies.json");
  allMovies = await response.json();
  displayMovies(allMovies);
}

// Filtering: return only movies whose names match the search text.
function getFilteredMovies(searchTerm) {
  const term = searchTerm.toLowerCase();
  return allMovies.filter((movie) =>
    movie.display_name.toLowerCase().includes(term),
  );
}

// Main catalog view: show movie cards and reset any player-specific layout.
function displayMovies(moviesToDisplay) {
  currentMovie = null;
  grid.classList.remove("player-mode");
  grid.innerHTML = "";

  moviesToDisplay.forEach((movie) => {
    grid.appendChild(createMovieCard(movie));
  });
}

// Movie card UI: create one clickable card for the grid.
function createMovieCard(movie) {
  const card = document.createElement("div");
  card.className = "movie-card";
  card.innerHTML = `
    <h3>${movie.display_name}</h3>
    <p>Year/Season: ${movie.year_or_season}</p>
    <span class="movie-badge">Type: ${movie.type}</span>
  `;

  card.onclick = async () => {
    const files = await fetchFolderContents(movie.full_path);
    renderFolderContents(movie, files);
  };

  return card;
}

// Folder data: ask the Flask route for the selected movie folder contents.
async function fetchFolderContents(folderPath) {
  const response = await fetch(
    `/list-contents?path=${encodeURIComponent(folderPath)}`,
  );
  const data = await response.json();
  return data.files || [];
}

// Folder view: replace the grid with the selected movie's file listing.
function renderFolderContents(movie, files) {
  currentMovie = movie;
  grid.classList.remove("player-mode");
  grid.innerHTML = `<h2>Contents of ${movie.display_name}</h2>`;
  grid.appendChild(createResultsBackButton());

  files.forEach((fileName) => {
    grid.appendChild(createFileItem(movie, fileName));
  });
}

// Folder navigation: return from file listing back to the filtered results.
function createResultsBackButton() {
  const backBtn = document.createElement("button");
  backBtn.className = "action-button";
  backBtn.innerText = "Back to Results";
  backBtn.onclick = () => {
    displayMovies(getFilteredMovies(searchInput.value));
  };
  return backBtn;
}

// File item UI: create one row and attach video playback when relevant.
function createFileItem(movie, fileName) {
  const fileItem = document.createElement("div");
  fileItem.className = "file-item";
  fileItem.innerText = fileName;

  if (isVideoFile(fileName)) {
    fileItem.classList.add("video-file");
    fileItem.onclick = () => {
      renderVideoPlayer(movie, fileName);
    };
  }

  return fileItem;
}

// Player view: swap the listing for an embedded browser video player.
function renderVideoPlayer(movie, fileName) {
  const videoUrl = `/stream-video?path=${encodeURIComponent(`${movie.full_path}\\${fileName}`)}`;
  const videoType = getVideoMimeType(fileName);

  grid.classList.add("player-mode");
  grid.innerHTML = `
    <div class="video-container">
      <button id="close-player" class="action-button">X</button>
      <video controls autoplay style="width: 100%; margin-top: 20px;">
        <source src="${videoUrl}" type="${videoType}">
        Your browser could not play this video directly.
      </video>
    </div>
  `;

  document.getElementById("close-player").onclick = async () => {
    if (!currentMovie) {
      displayMovies(getFilteredMovies(searchInput.value));
      return;
    }

    const files = await fetchFolderContents(currentMovie.full_path);
    renderFolderContents(currentMovie, files);
  };
}

// File type check: decide whether a file should be treated as playable video.
function isVideoFile(fileName) {
  const lowerName = fileName.toLowerCase();
  return lowerName.endsWith(".mp4") || lowerName.endsWith(".mkv");
}

// MIME helper: send the browser the most appropriate video type string.
function getVideoMimeType(fileName) {
  const lowerName = fileName.toLowerCase();

  if (lowerName.endsWith(".mp4")) {
    return "video/mp4";
  }

  if (lowerName.endsWith(".mkv")) {
    return "video/x-matroska";
  }

  return "";
}
