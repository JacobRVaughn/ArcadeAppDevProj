<?php
header("Content-Type: application/json");

$conn = new mysqli("localhost", "root", "", "arcade_db");

// game key
$game = isset($_GET['game']) ? trim($_GET['game']) : '';

// Return leaderboard for that game key, else return users by xp
if ($game !== '') {
    // Prepared statement to avoid injection
    $stmt = $conn->prepare(
        "SELECT u.id AS user_id, u.username AS name, u.xp AS xp, MAX(gs.score) AS score
         FROM game_scores gs
         JOIN users u ON u.id = gs.user_id
         WHERE gs.game_key = ?
         GROUP BY u.id
         ORDER BY score DESC
         LIMIT 100"
    );
    $stmt->bind_param('s', $game);
    $stmt->execute();
    $res = $stmt->get_result();

    $users = [];
    while ($row = $res->fetch_assoc()) {
        $users[] = [
            "id" => (int)$row["user_id"],
            "name" => $row["name"],
            "xp" => isset($row["xp"]) ? (int)$row["xp"] : 0,
            "score" => isset($row["score"]) ? (int)$row["score"] : 0
        ];
    }

    echo json_encode($users);
    $stmt->close();
} else {
    $stmt = $conn->prepare("SELECT id, username, xp FROM users ORDER BY xp DESC LIMIT 100");
    $stmt->execute();
    $res = $stmt->get_result();

    $users = [];
    while ($row = $res->fetch_assoc()) {
        $users[] = [
            "id" => (int)$row["id"],
            "name" => $row["username"],
            "xp" => isset($row["xp"]) ? (int)$row["xp"] : 0
        ];
    }

    echo json_encode($users);
    $stmt->close();
}

$conn->close();
?>