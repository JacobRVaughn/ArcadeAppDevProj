<?php
/**
 * save_game_result.php
 * Called via fetch() from the game's game-over screen.
 *
 * Expects JSON body:
 *   { "game_id": "math-catch", "score": 1450, "xp_earned": 300 }
 *
 * Returns JSON:
 *   { "status":"ok", "xp_before":200, "xp_after":500, "level_before":1, "level_after":1, "leveled_up":false }
 */

header("Content-Type: application/json");
session_start();

// ── Auth check ───────────────────────────────────────────────────────────────
if (!isset($_SESSION['logged_in']) || !$_SESSION['logged_in']) {
    http_response_code(401);
    echo json_encode(["status" => "error", "message" => "Not logged in."]);
    exit;
}

// ── Parse body ───────────────────────────────────────────────────────────────
$body     = json_decode(file_get_contents("php://input"), true);
$game_id  = trim($body["game_id"]  ?? "");
$score    = (int)($body["score"]   ?? 0);
$xp_award = (int)($body["xp_earned"] ?? 0);
$user_id  = (int)$_SESSION['user_id'];

if ($game_id === "" || $score < 0 || $xp_award < 0) {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Invalid payload."]);
    exit;
}

// Cap XP per request so the client can't inflate it
$MAX_XP = 1000;
$xp_award = min($xp_award, $MAX_XP);

// ── DB ───────────────────────────────────────────────────────────────────────
$conn = new mysqli("localhost", "root", "", "arcade_db");
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["status" => "error", "message" => "DB connection failed."]);
    exit;
}

// Helper: XP threshold per level (1000 XP per level)
function xp_to_level(int $xp): int {
    return (int)floor($xp / 1000) + 1;
}

// ── Fetch current XP ─────────────────────────────────────────────────────────
$stmt = $conn->prepare("SELECT xp FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$row) {
    http_response_code(404);
    echo json_encode(["status" => "error", "message" => "User not found."]);
    exit;
}

$xp_before    = (int)$row["xp"];
$xp_after     = $xp_before + $xp_award;
$level_before = xp_to_level($xp_before);
$level_after  = xp_to_level($xp_after);
$leveled_up   = $level_after > $level_before;

// ── Update XP ────────────────────────────────────────────────────────────────
$stmt = $conn->prepare("UPDATE users SET xp = ? WHERE id = ?");
$stmt->bind_param("ii", $xp_after, $user_id);
$stmt->execute();
$stmt->close();

// ── Insert score row ─────────────────────────────────────────────────────────
// Expects a scores table:
//   CREATE TABLE IF NOT EXISTS scores (
//     id         INT AUTO_INCREMENT PRIMARY KEY,
//     user_id    INT          NOT NULL,
//     game_id    VARCHAR(64)  NOT NULL,
//     score      INT          NOT NULL DEFAULT 0,
//     xp_earned  INT          NOT NULL DEFAULT 0,
//     played_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
//     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
//   );
$stmt = $conn->prepare(
    "INSERT INTO scores (user_id, game_id, score, xp_earned) VALUES (?, ?, ?, ?)"
);
$stmt->bind_param("isii", $user_id, $game_id, $score, $xp_award);
$stmt->execute();
$stmt->close();

$conn->close();

// ── Respond ───────────────────────────────────────────────────────────────────
echo json_encode([
    "status"       => "ok",
    "xp_before"    => $xp_before,
    "xp_after"     => $xp_after,
    "xp_earned"    => $xp_award,
    "level_before" => $level_before,
    "level_after"  => $level_after,
    "leveled_up"   => $leveled_up,
]);