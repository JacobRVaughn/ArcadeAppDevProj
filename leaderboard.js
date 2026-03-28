document.addEventListener("DOMContentLoaded", () => {
  const openButton = document.getElementById("viewAllButton");
  const fullLeaderboard = document.getElementById("fullLeaderboard");
  const closeButton = document.getElementById("closeFullLeaderboard");
  const fullRoster = document.getElementById("fullRoster");
  const topRoster = document.getElementById("roster");
  const headerTitle = document.getElementById("leaderboardGameTitle");

  // Get current game key
  const gameKey = getGameKey();

  let users = [];

  // Set leaderboard header title
  if (headerTitle) {
    headerTitle.textContent = gameKey
      ? `LEADERBOARD — ${gameKey}`
      : "LEADERBOARD";
  }

  // Determine which game the leaderboard should load
  function getGameKey() {
    // Global variable if it exists
    if (window.LEADERBOARD_GAME_KEY) return String(window.LEADERBOARD_GAME_KEY);

    // Otherwise, get ?game= from the URL
    try {
      const params = new URLSearchParams(window.location.search);
      if (params.has("game")) return params.get("game");
    } catch (e) {
    }
    // No game key found
    return "";
  }

  // Get the numeric value to rank by
  function getValue(user) {
    return gameKey ? Number(user.score || 0) : Number(user.xp || 0);
  }

  // Format value
  function formatValue(n) {
    return `${Number(n).toLocaleString()} XP`;
  }


  // Avoid usernames injecting unsafe markup
  function escapeHtml(str) {
    if (typeof str !== "string") return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Create a leaderboard row element for user
  function createRow(user, rank) {
    const row = document.createElement("div");
    row.className = "leaderboard-roster-row";
    row.setAttribute("role", "listitem");

    // Highlight top player and current user
    if (rank === 1) row.classList.add("leaderboard-row-top");
    if (user.you) row.classList.add("leaderboard-row-you");

    // Get avatar letter
    const avatarLetter = user.name
      ? user.name.trim().charAt(0).toUpperCase()
      : "?";

    const value = getValue(user);

    row.innerHTML = `
      <div class="leaderboard-roster-left">
        <div class="leaderboard-rank-bubble">${rank}</div>
        <div class="leaderboard-avatar">${avatarLetter}</div>
        <div class="leaderboard-meta">
          <div class="leaderboard-name">
            ${escapeHtml(user.name)}
            ${user.you ? '<span class="leaderboard-you-badge">YOU</span>' : ''}
          </div>
        </div>
      </div>
      <div class="leaderboard-xp">${formatValue(value)}</div>
    `;

    return row;
  }

  // Fetch leaderboard data
  async function fetchLeaderboard() {
    const url = gameKey
      ? `get_leaderboard.php?game=${encodeURIComponent(gameKey)}`
      : "get_leaderboard.php";

    try {
      const response = await fetch(url);
      users = await response.json();
    } catch (err) {
      console.error("Failed to fetch leaderboard:", err);
      users = [];
    }

    // Populate top 3
    populateTop3();
  }

  // Return users sorted by highest value first
  function getSortedUsers() {
    return [...users].sort((a, b) => getValue(b) - getValue(a));
  }

  // Populate full leaderboard
  function populateFullLeaderboard() {
    if (!fullRoster) return;

    fullRoster.innerHTML = "";
    const sorted = getSortedUsers();

    // Add all users to full leaderboard
    sorted.forEach((user, idx) => {
      fullRoster.appendChild(createRow(user, idx + 1));
    });
  }

  // Populate top 3 leaderboard
  function populateTop3() {
    if (!topRoster) return;

    topRoster.innerHTML = "";
    const sorted = getSortedUsers();

    // Get top 3 users
    const top3 = sorted.slice(0, 3);

    top3.forEach((user, idx) => {
      topRoster.appendChild(createRow(user, idx + 1));
    });

    // Current user is shown even if not in top 3
    const youIndex = sorted.findIndex(u => u.you === true);
    if (youIndex !== -1) {
      const youRank = youIndex + 1;
      const youUser = sorted[youIndex];

      // Only add if outside top 3
      if (youRank > 3) {
        const youRow = createRow(youUser, youRank);
        topRoster.appendChild(youRow);
      }
    }
  }

  // Open full leaderboard
  function openFullLeaderboard() {
    populateFullLeaderboard();
    fullLeaderboard.classList.add("active");
    fullLeaderboard.setAttribute("aria-hidden", "false");
  }

  // Close full leaderboard
  function closeFullLeaderboard() {
    fullLeaderboard.classList.remove("active");
    fullLeaderboard.setAttribute("aria-hidden", "true");
  }

  // Open on button click
  if (openButton) {
    openButton.addEventListener("click", (e) => {
      e.preventDefault();
      openFullLeaderboard();
    });
  }

  // Close on close button click
  if (closeButton) {
    closeButton.addEventListener("click", (e) => {
      e.preventDefault();
      closeFullLeaderboard();
    });
  }

  // Close when clicking outside content
  if (fullLeaderboard) {
    fullLeaderboard.addEventListener("click", (e) => {
      if (e.target === fullLeaderboard) closeFullLeaderboard();
    });
  }

  // Close when pressing Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeFullLeaderboard();
  });

  fetchLeaderboard();
});