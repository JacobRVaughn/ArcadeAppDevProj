document.addEventListener("DOMContentLoaded", () => {
    const studentBox = document.getElementById("studentBox");
    const studentName = document.getElementById("studentName");
    const studentXp = document.getElementById("studentXp");
    const miniRank = document.getElementById("miniRank");
    const miniScore = document.getElementById("miniScore");

    // Get the current game key
    const gameKey = getGameKey();

    let users = [];

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

    // Return array sorted from highest to lowest
    function getSortedUsers() {
        return [...users].sort((a, b) => getValue(b) - getValue(a));
    }

    // Use first letter as avatar
    function getAvatarLetter(user) {
        return user.name ? user.name.trim().charAt(0).toUpperCase() : "?";
    }

    // Find the current signed in user, fallback is top user
    function getYouUser(sorted) {
        return sorted.find(u => u.you === true) || sorted[0] || null;
    }

    // Get the rank position of a specific user in the sorted list
    function getRankOfUser(sorted, user) {
        if (!user) return "-";

        const idx = sorted.findIndex(
            u => u.name === user.name && getValue(u) === getValue(user)
        );

        return idx === -1 ? "-" : idx + 1;
    }

    // Fetch leaderboard data from the server
    async function fetchLeaderboardData() {
        const url = gameKey
            ? `get_leaderboard.php?game=${encodeURIComponent(gameKey)}`
            : "get_leaderboard.php";

        try {
            const response = await fetch(url);
            users = await response.json();
        } catch (error) {
            console.error("Failed to fetch leaderboard data:", error);
            users = [];
        }

        // Update both leaderboard displays after loading
        populateStudentBox();
        populateMiniLeaderboard();
    }

    // Fills in student card on navigation bar with user info
    function populateStudentBox() {
        if (!studentBox) return;

        const sorted = getSortedUsers();
        const youUser = getYouUser(sorted);
        if (!youUser) return;

        const avatarLetter = getAvatarLetter(youUser);
        const rank = getRankOfUser(sorted, youUser);
        const value = getValue(youUser);

        // Update avatar letter
        const avatar = studentBox.querySelector(".leaderboard-avatar");
        if (avatar) avatar.textContent = avatarLetter;

        // Update name
        if (studentName) {
            studentName.innerHTML = escapeHtml(youUser.name);
        }

        // Update rank and xp
        if (studentXp) {
            studentXp.textContent = gameKey
                ? `Rank ${rank} · ${formatValue(value)}`
                : `Rank ${rank} · Level 1`;
        }
    }

    // Fills in mini leaderboard display on navigation bar
    function populateMiniLeaderboard() {
        const sorted = getSortedUsers();
        const youUser = getYouUser(sorted);
        if (!youUser) return;

        const rank = getRankOfUser(sorted, youUser);
        const value = getValue(youUser);

        if (miniRank) miniRank.textContent = `#${rank}`;
        if (miniScore) miniScore.textContent = formatValue(value);
    }

    // click the box to return to the dashboard
    if (studentBox) {
        studentBox.addEventListener("click", () => {
            const goDashboard = confirm(
                "Would you like to return to the student dashboard?"
            );

            if (goDashboard) {
                window.location.href = "student-dashboard.php";
            }
        });
    }

    fetchLeaderboardData();
});