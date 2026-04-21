<?php
// classes_api.php
// Place this file on your server and set DB credentials below.
// Handles: GET /classes_api.php        → list all classes
//          POST /classes_api.php       → create a class { name, code }
//          DELETE /classes_api.php?id= → delete a class by id

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *"); // tighten this in production
header("Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") { http_response_code(204); exit; }

$conn = new mysqli("localhost", "root", "", "arcade_db");

if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "DB connection failed"]);
    exit;
}

$method = $_SERVER["REQUEST_METHOD"];

// GET — return all classes
if ($method === "GET") {
    $result = $conn->query("SELECT id, code, name FROM classes ORDER BY id DESC");
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
    }
    echo json_encode(["classes" => $rows]);
    exit;
}

// POST — create a class
if ($method === "POST") {
    $body = json_decode(file_get_contents("php://input"), true);
    $name = trim($body["name"] ?? "");
    $code = trim($body["code"] ?? "");

    if (!$name || !$code) {
        http_response_code(400);
        echo json_encode(["error" => "name and code are required"]);
        exit;
    }

    // Ensure code is unique
    $check = $conn->prepare("SELECT id FROM classes WHERE code = ?");
    $check->bind_param("s", $code);
    $check->execute();
    $check->store_result();
    if ($check->num_rows > 0) {
        http_response_code(409);
        echo json_encode(["error" => "code_collision"]);
        exit;
    }

    $stmt = $conn->prepare("INSERT INTO classes (code, name) VALUES (?, ?)");
    $stmt->bind_param("ss", $code, $name);
    $stmt->execute();
    $newId = $conn->insert_id;

    http_response_code(201);
    echo json_encode(["class" => ["id" => $newId, "code" => $code, "name" => $name]]);
    exit;
}

// DELETE — remove a class
if ($method === "DELETE") {
    $id = intval($_GET["id"] ?? 0);
    if (!$id) {
        http_response_code(400);
        echo json_encode(["error" => "id required"]);
        exit;
    }
    $stmt = $conn->prepare("DELETE FROM classes WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    echo json_encode(["deleted" => $id]);
    exit;
}

http_response_code(405);
echo json_encode(["error" => "Method not allowed"]);
