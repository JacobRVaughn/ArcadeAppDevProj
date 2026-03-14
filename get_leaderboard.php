<?php
header("Content-Type: application/json");
session_start();

$conn = new mysqli("localhost", "root", "", "arcade_db");
$current_user_id = $_SESSION['user_id'] ?? null;

$sql = "SELECT id, username, xp FROM users ORDER BY xp DESC";
$result = $conn->query($sql);

$users = [];
while ($row = $result->fetch_assoc()) {
    $users[] = [
        "name" => $row["username"],
        "xp"   => (int)$row["xp"],
        "you"  => ($row["id"] == $current_user_id)
    ];
}

echo json_encode($users);
$conn->close();
?>