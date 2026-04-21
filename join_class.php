<?php
session_start();
if (!isset($_SESSION['logged_in']) || !$_SESSION['logged_in'] || $_SESSION['role'] !== 'student') {
    http_response_code(401);
    echo json_encode(["error" => "Unauthorized"]);
    exit;
}

header("Content-Type: application/json");

$conn = new mysqli("localhost", "root", "", "arcade_db");

if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "DB connection failed"]);
    exit;
}

$method = $_SERVER["REQUEST_METHOD"];
$userId = $_SESSION['user_id'];

// GET — return the student's current class (if any)
if ($method === "GET") {
    $stmt = $conn->prepare("
        SELECT c.id, c.name, c.code
        FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.id = ?
    ");
    $stmt->bind_param("i", $userId);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();

    if (isset($row["id"]) && $row["id"] !== null) {
        echo json_encode(["class" => ["id" => $row["id"], "name" => $row["name"], "code" => $row["code"]]]);
    } else {
        echo json_encode(["class" => null]);
    }
    exit;
}

// POST — join a class by code
if ($method === "POST") {
    $body = json_decode(file_get_contents("php://input"), true);
    $code = strtoupper(trim($body["code"] ?? ""));

    if (!$code) {
        http_response_code(400);
        echo json_encode(["error" => "Code is required."]);
        exit;
    }

    // Look up the class
    $stmt = $conn->prepare("SELECT id, name FROM classes WHERE code = ?");
    $stmt->bind_param("s", $code);
    $stmt->execute();
    $class = $stmt->get_result()->fetch_assoc();

    if (!$class) {
        http_response_code(404);
        echo json_encode(["error" => "No class found with that code."]);
        exit;
    }

    // Assign class to student
    $update = $conn->prepare("UPDATE users SET class_id = ? WHERE id = ?");
    $update->bind_param("ii", $class["id"], $userId);
    $update->execute();

    echo json_encode(["class" => ["id" => $class["id"], "name" => $class["name"], "code" => $code]]);
    exit;
}

// POST to leave — separate action via ?action=leave
if ($method === "DELETE") {
    $update = $conn->prepare("UPDATE users SET class_id = NULL WHERE id = ?");
    $update->bind_param("i", $userId);
    $update->execute();
    echo json_encode(["class" => null]);
    exit;
}

http_response_code(405);
echo json_encode(["error" => "Method not allowed"]);
