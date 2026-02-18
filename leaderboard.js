document.addEventListener("DOMContentLoaded", () => {
    const openButton = document.getElementById("viewAllButton");
    const fullLeaderboard = document.getElementById("fullLeaderboard");
    const closeButton = document.getElementById("closeFullLeaderboard");
    const fullRoster = document.getElementById("fullRoster");
    const topRoster = document.getElementById("roster");
  
    // Example users. TODO: replace with data from DB
    const users = [
      { name: "A_user", xp: 15000 },
      { name: "B_user", xp: 13750 },
      { name: "C_user", xp: 10500 },
      { name: "D_user", xp: 9800 },
      { name: "You", xp: 1600, you: true }, // current user
      { name: "E_user", xp: 8700 },
      { name: "F_user", xp: 8200 },
      { name: "G_user", xp: 7900 },
      { name: "H_user", xp: 7600 },
      { name: "I_user", xp: 7200 },
    ];
  
    function formatXP(n) {
      return `${Number(n).toLocaleString()} XP`;
    }

    function createRow(user, rank) {
      const row = document.createElement("div");
      row.className = "leaderboard-roster-row";
  
      if (rank === 1) row.classList.add("leaderboard-row-top");
      if (user.you) row.classList.add("leaderboard-row-you");
  
      // Use first character of username as avatar letter
      const avatarLetter = user.name ? user.name.trim().charAt(0).toUpperCase() : "?";
  
      row.innerHTML = `
        <div class="leaderboard-roster-left">
          <div class="leaderboard-rank-bubble">${rank}</div>
          <div class="leaderboard-avatar">${avatarLetter}</div>
          <div class="leaderboard-meta">
            <div class="leaderboard-name">
              ${escapeHtml(user.name)}
              ${user.you ? '<span class="leaderboard-you-badge">YOU</span>' : ''}
            </div>
            <div class="leaderboard-xp">${formatXP(user.xp)}</div>
          </div>
        </div>
        <div class="leaderboard-xp">${formatXP(user.xp)}</div>
      `;
  
      return row;
    }

    function escapeHtml(str) {
      if (typeof str !== "string") return "";
      return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
  
    // Populate the full leaderboard
    function populateFullLeaderboard() {
      fullRoster.innerHTML = "";
      const sorted = [...users].sort((a, b) => b.xp - a.xp);
  
      sorted.forEach((user, idx) => {
        fullRoster.appendChild(createRow(user, idx + 1));
      });
    }
  
    // Populate the top 3 area. If current user isn't top 3, append them
    function populateTop3() {
      topRoster.innerHTML = "";
  
      const sorted = [...users].sort((a, b) => b.xp - a.xp);
      const top3 = sorted.slice(0, 3);
  
      // Append top 3 rows
      top3.forEach((user, idx) => {
        topRoster.appendChild(createRow(user, idx + 1));
      });
  
      // Find current user
      const youIndex = sorted.findIndex(u => u.you === true);
      if (youIndex !== -1) {
        const youRank = youIndex + 1;
        const youUser = sorted[youIndex];
  
        if (youRank > 3) {
          const youRow = createRow(youUser, youRank);
          if (!youRow.classList.contains("leaderboard-row-you")) {
            youRow.classList.add("leaderboard-row-you");
          }
          topRoster.appendChild(youRow);
        }
      }
    }
    
    function openFullLeaderboard() {
      populateFullLeaderboard();
      fullLeaderboard.classList.add("active");
      fullLeaderboard.setAttribute("aria-hidden", "false");
    }
  
    function closeFullLeaderboard() {
      fullLeaderboard.classList.remove("active");
      fullLeaderboard.setAttribute("aria-hidden", "true");
    }
  
    if (openButton) {
      openButton.addEventListener("click", (e) => {
        e.preventDefault();
        openFullLeaderboard();
      });
    }
  
    if (closeButton) {
      closeButton.addEventListener("click", (e) => {
        e.preventDefault();
        closeFullLeaderboard();
      });
    }
  
    // click outside to close
    if (fullLeaderboard) {
      fullLeaderboard.addEventListener("click", (e) => {
        if (e.target === fullLeaderboard) closeFullLeaderboard();
      });
    }
  
    // ESC to close
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeFullLeaderboard();
    });

    populateTop3();
  });