<?php
header("Content-Type: application/json");

session_start();


if ($conn->connect_error) {
    http_response_code(500); 
    echo json_encode(["error" => "Database connection failed"]);
    exit;
}

// Get current signed in user ID
$current_user_id = $_SESSION['user_id'] ?? null;

// Get game key from URL
$game = isset($_GET['game']) ? trim($_GET['game']) : '';

/*
|--------------------------------------------------------------------------
| GAME  LEADERBOARD
|--------------------------------------------------------------------------
*/
if ($game !== '') {

    // get each user's highest score for the selected game
    $stmt = $conn->prepare(
        "SELECT u.id AS user_id, u.username AS name, u.xp AS xp, MAX(s.score) AS score
         FROM scores s
         JOIN users u ON u.id = s.user_id
         WHERE s.game_id = ?
         GROUP BY u.id, u.username, u.xp
         ORDER BY score DESC
         LIMIT 100"
    );
    $stmt->bind_param('s', $game);
    $stmt->execute();
    $res = $stmt->get_result();

    $users = [];
    while ($row = $res->fetch_assoc()) {
        $users[] = [
            "id"    => (int)$row["user_id"],   // User ID
            "name"  => $row["name"],          // Username
            "xp"    => (int)$row["xp"],       // Total XP
            "score" => (int)$row["score"],    // Best score for game
            "you"   => ((int)$row["user_id"] === (int)$current_user_id) // Is current user?
        ];
    }

    echo json_encode($users);

    $stmt->close();

/*
|--------------------------------------------------------------------------
| GLOBAL LEADERBOARD
|--------------------------------------------------------------------------
*/
} else {

    // get top users ranked by XP
    $stmt = $conn->prepare(
        "SELECT id, username, xp FROM users ORDER BY xp DESC LIMIT 100"
    );

    $stmt->execute();
    $res = $stmt->get_result();

    $users = [];

    while ($row = $res->fetch_assoc()) {
        $users[] = [
            "id"   => (int)$row["id"],         // User ID
            "name" => $row["username"],       // Username
            "xp"   => (int)$row["xp"],        // XP value
            "you"  => ((int)$row["id"] === (int)$current_user_id) // Is current user?
        ];
    }

    echo json_encode($users);

    $stmt->close();
}

$conn->close();
?>