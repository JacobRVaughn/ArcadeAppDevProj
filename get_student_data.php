<?php
header("Content-Type: application/json");
session_start();

if (!isset($_SESSION['logged_in']) || !$_SESSION['logged_in']) {
    echo json_encode(["error" => "unauthorized"]);
    exit;
}

$conn = new mysqli("localhost", "root", "", "arcade_db");
$user_id = $_SESSION['user_id'];

// Fetch current student
$stmt = $conn->prepare("SELECT username, xp FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$student = $stmt->get_result()->fetch_assoc();

// Fetch top 5 leaderboard
$top5Result = $conn->query("SELECT username, xp FROM users ORDER BY xp DESC LIMIT 5");
$top5 = [];
while ($row = $top5Result->fetch_assoc()) {
    $top5[] = ["username" => $row["username"], "score" => (int)$row["xp"]];
}

echo json_encode([
    "student" => [
        "username" => $student["username"],
        "xp"       => (int)$student["xp"],
        "points"   => (int)$student["xp"],   // map xp to points, or add a separate column
        "accuracy" => 0                        // add an accuracy column to DB later
    ],
    "topFive" => $top5
]);

$conn->close();
?>