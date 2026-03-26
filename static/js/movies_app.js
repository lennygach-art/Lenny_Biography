const grid = document.getElementById("movie-grid");
const searchInput = document.getElementById("movie-search");
const catalogCount = document.getElementById("catalog-count");

let allMovies = [];
let currentMovie = null;

initializePage();

async function initializePage() {
  attachKeyboardShortcuts();
  attachSearchListener();
  await loadMovies();
}

function attachKeyboardShortcuts() {
  document.addEventListener(
    "keydown",
    (event) => {
      const activeVideo = document.getElementById("main-video");
      if (!activeVideo) {
        return;
      }

      if (event.code === "Space") {
        event.preventDefault();
        togglePlay();
        return;
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();
        activeVideo.currentTime += 10;
        return;
      }

      if (event.key === "ArrowLeft") {
        event.preventDefault();
        activeVideo.currentTime -= 10;
      }
    },
    true,
  );
}

function attachSearchListener() {
  searchInput.addEventListener("input", () => {
    displayMovies(getFilteredMovies(searchInput.value));
  });
}

async function loadMovies() {
  const response = await fetch("/api/catalog");
  allMovies = await response.json();
  updateCatalogCount(allMovies.length);
  displayMovies(allMovies);
}

function getFilteredMovies(searchTerm) {
  const term = searchTerm.toLowerCase();
  return allMovies.filter((movie) =>
    movie.display_name.toLowerCase().includes(term),
  );
}

function displayMovies(moviesToDisplay) {
  currentMovie = null;
  grid.classList.remove("player-mode");
  grid.innerHTML = "";
  updateCatalogCount(
    moviesToDisplay.length,
    moviesToDisplay.length === allMovies.length ? "titles available" : "matching results",
  );

  moviesToDisplay.forEach((movie) => {
    grid.appendChild(createMovieCard(movie));
  });
}

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

async function fetchFolderContents(folderPath) {
  const response = await fetch(
    `/list-contents?path=${encodeURIComponent(folderPath)}`,
  );
  const data = await response.json();
  return data.files || [];
}

function renderFolderContents(movie, files) {
  currentMovie = movie;
  grid.classList.remove("player-mode");
  grid.innerHTML = `<h2 class="catalog-section-title">Contents of ${movie.display_name}</h2>`;
  updateCatalogCount(files.length, "items in folder");
  grid.appendChild(createResultsBackButton());

  files.forEach((fileName) => {
    grid.appendChild(createFileItem(movie, fileName));
  });
}

function createResultsBackButton() {
  const backBtn = document.createElement("button");
  backBtn.className = "catalog-back-link";
  backBtn.innerText = "Back to Results";
  backBtn.onclick = () => {
    displayMovies(getFilteredMovies(searchInput.value));
  };
  return backBtn;
}

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

function renderVideoPlayer(movie, fileName) {
  const videoUrl = `/stream-video?path=${encodeURIComponent(`${movie.full_path}\\${fileName}`)}`;
  const videoType = getVideoMimeType(fileName);

  grid.classList.add("player-mode");
  updateCatalogCount(fileName, "now playing");
  grid.innerHTML = `
    <div class="video-container">
      <div class="player-toolbar">
        <button id="close-player" class="catalog-back-link">Back to Files</button>
      </div>
      <div class="video-wrapper">
        <video id="main-video" controls autoplay>
          <source src="${videoUrl}" type="${videoType}">
          Your browser could not play this video directly.
        </video>
      </div>
    </div>
  `;

  document.getElementById("main-video").onclick = togglePlay;

  document.getElementById("close-player").onclick = async () => {
    if (!currentMovie) {
      displayMovies(getFilteredMovies(searchInput.value));
      return;
    }

    const files = await fetchFolderContents(currentMovie.full_path);
    renderFolderContents(currentMovie, files);
  };
}

function updateCatalogCount(value, label = "titles available") {
  if (!catalogCount) {
    return;
  }

  catalogCount.textContent = `${value} ${label}`;
}

function togglePlay() {
  const video = document.getElementById("main-video");
  if (!video) {
    return;
  }

  if (video.paused) {
    video.play();
  } else {
    video.pause();
  }
}

function isVideoFile(fileName) {
  const lowerName = fileName.toLowerCase();
  return lowerName.endsWith(".mp4") || lowerName.endsWith(".mkv");
}

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
