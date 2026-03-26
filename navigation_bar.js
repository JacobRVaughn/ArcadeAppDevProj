document.addEventListener("DOMContentLoaded", () => {
    const studentBox = document.getElementById("studentBox");
    const studentName = document.getElementById("studentName");
    const studentXp = document.getElementById("studentXp");
    const miniRank = document.getElementById("miniRank");
    const miniScore = document.getElementById("miniScore");

    let users = [];

    // Gets XP and username
    async function fetchLeaderboardData() {
        const response = await fetch("get_leaderboard.php");

        users = await response.json();
        populateStudentBox();
        populateMiniLeaderboard();
    }

    function getSortedUsers() {
        return [...users].sort((a, b) => b.xp - a.xp);
    }

    function formatXP(n) {
        return `${Number(n).toLocaleString()} XP`;
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

    // Use first character of username as avatar letter
    function getAvatarLetter(user) {
        return user.name ? user.name.trim().charAt(0).toUpperCase() : "?";
    }

    function getYouUser(sorted) {
        return sorted.find(u => u.you === true) || sorted[0] || null;
    }

    function getRankOfUser(sorted, user) {
        if (!user) return "-";
        const idx = sorted.findIndex(u => u.name === user.name && u.xp === user.xp);
        return idx === -1 ? "-" : idx + 1;
    }

    function populateStudentBox() {
        if (!studentBox) return;

        const sorted = getSortedUsers();
        const youUser = getYouUser(sorted);
        if (!youUser) return;

        const avatarLetter = getAvatarLetter(youUser);
        const rank = getRankOfUser(sorted, youUser);

        const avatar = studentBox.querySelector(".leaderboard-avatar");
        if (avatar) avatar.textContent = avatarLetter;

        if (studentName) {
            studentName.innerHTML = `
        ${escapeHtml(youUser.name)}
      `;
        }

        if (studentXp) {
            studentXp.textContent = `Rank ${rank} · Level 1`;
        }
    }

    // Mini "leaderboard" that shows only the current student
    function populateMiniLeaderboard() {
        const sorted = getSortedUsers();
        const youUser = getYouUser(sorted);
        if (!youUser) return;

        const rank = getRankOfUser(sorted, youUser);

        if (miniRank) miniRank.textContent = `#${rank}`;
        if (miniScore) miniScore.textContent = formatXP(youUser.xp);
    }

    if (studentBox) {
        studentBox.addEventListener("click", () => {
            const goDashboard = confirm("Would you like to return to the student dashboard?");
            if (goDashboard) {
                window.location.href = "student-dashboard.php";
            }
        });
    }

    fetchLeaderboardData();
});