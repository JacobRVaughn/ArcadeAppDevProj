<?php
header("Content-Type: application/json");

$conn = new mysqli("localhost", "root", "", "arcade_db");

$sql = "SELECT username, xp FROM users ORDER BY xp DESC";
$result = $conn->query($sql);

$users = [];

while ($row = $result->fetch_assoc()) {
    $users[] = [
        "name" => $row["username"],
        "xp" => (int)$row["xp"]
    ];
}

echo json_encode($users);

$conn->close();
?>