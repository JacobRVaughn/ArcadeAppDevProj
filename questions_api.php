<?php
/**
 * questions_api.php — EduQuest Arcade custom question bank
 *
 * GET    ?action=setup          → test DB connection & auto-create table
 * GET                           → list all questions
 * POST                          → create a question
 * DELETE ?id=<id>               → delete a question
 */

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") {
    http_response_code(204);
    exit;
}

// ── DB config ────────────────────────────
define("DB_HOST",    "localhost");
define("DB_NAME",    "arcade_db");   
define("DB_USER",    "root");       
define("DB_PASS",    "");         
define("DB_CHARSET", "utf8mb4");

// Set to false on production to hide raw error details from the browser
define("DEV_MODE", true);

// ── Helpers ─────────────────────────────────────────────────────────────────
function jsonOk(array $data, int $code = 200): void {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function jsonErr(string $msg, int $code = 400, array $debug = []): void {
    http_response_code($code);
    $payload = ["error" => $msg];
    if (DEV_MODE && $debug) {
        $payload["debug"] = $debug;
    }
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function sanitizeStr(string $s, int $max = 300): string {
    return mb_substr(trim(strip_tags($s)), 0, $max);
}

// ── DB connection ────────────────────────────────────────────────────────────
function getDB(): PDO {
    static $pdo = null;
    if ($pdo) return $pdo;
    $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
    $pdo = new PDO($dsn, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ]);
    return $pdo;
}

// ── Auto-create table (no foreign key constraint to avoid classes table issues) ──
function ensureTable(PDO $db): void {
    $db->exec("
        CREATE TABLE IF NOT EXISTS custom_questions (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            class_id       INT          NULL,
            question       TEXT         NOT NULL,
            correct_answer VARCHAR(255) NOT NULL,
            wrong_answer_1 VARCHAR(255) NOT NULL,
            wrong_answer_2 VARCHAR(255) NOT NULL,
            wrong_answer_3 VARCHAR(255) NOT NULL,
            category       VARCHAR(80)  NOT NULL DEFAULT '',
            created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ");
}

// ── Router ───────────────────────────────────────────────────────────────────
$method = $_SERVER["REQUEST_METHOD"];

try {
    $db = getDB();
    ensureTable($db);

    // ── GET ?action=setup — diagnostic ──────────────────────────────────────
    if ($method === "GET" && ($_GET["action"] ?? "") === "setup") {
        $tables = $db->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
        $qCount = (int) $db->query("SELECT COUNT(*) FROM custom_questions")->fetchColumn();
        jsonOk([
            "status"          => "ok",
            "db_name"         => DB_NAME,
            "tables_found"    => $tables,
            "questions_table" => in_array("custom_questions", $tables) ? "exists" : "missing",
            "question_count"  => $qCount,
            "php_version"     => PHP_VERSION,
        ]);
    }

    // ── GET — list questions ─────────────────────────────────────────────────
    if ($method === "GET") {
        $rows = $db->query("
            SELECT id, class_id, question, correct_answer,
                   wrong_answer_1, wrong_answer_2, wrong_answer_3,
                   category, created_at
            FROM custom_questions
            ORDER BY created_at DESC
        ")->fetchAll();

        foreach ($rows as &$r) {
            $r["id"]       = (int) $r["id"];
            $r["class_id"] = $r["class_id"] !== null ? (int) $r["class_id"] : null;
        }
        unset($r);

        jsonOk(["questions" => $rows]);
    }

    // ── POST — create question ───────────────────────────────────────────────
    if ($method === "POST") {
        $raw  = file_get_contents("php://input");
        $body = json_decode($raw, true);

        if (!is_array($body)) {
            jsonErr("Invalid JSON body. Received: " . substr($raw, 0, 120), 400);
        }

        $question       = sanitizeStr($body["question"]       ?? "", 500);
        $correct_answer = sanitizeStr($body["correct_answer"] ?? "", 255);
        $wrong_answer_1 = sanitizeStr($body["wrong_answer_1"] ?? "", 255);
        $wrong_answer_2 = sanitizeStr($body["wrong_answer_2"] ?? "", 255);
        $wrong_answer_3 = sanitizeStr($body["wrong_answer_3"] ?? "", 255);
        $category       = sanitizeStr($body["category"]       ?? "", 80);

        // class_id: accept null, empty string, or integer
        $rawClassId = $body["class_id"] ?? null;
        $class_id   = ($rawClassId !== null && $rawClassId !== "") ? (int) $rawClassId : null;

        // Validate required fields
        $missing = [];
        if ($question       === "") $missing[] = "question";
        if ($correct_answer === "") $missing[] = "correct_answer";
        if ($wrong_answer_1 === "") $missing[] = "wrong_answer_1";
        if ($wrong_answer_2 === "") $missing[] = "wrong_answer_2";
        if ($wrong_answer_3 === "") $missing[] = "wrong_answer_3";
        if ($missing) {
            jsonErr("Missing required fields: " . implode(", ", $missing), 422);
        }

        // Soft-check class_id — skip if classes table doesn't exist yet
        if ($class_id !== null) {
            try {
                $check = $db->prepare("SELECT id FROM classes WHERE id = ?");
                $check->execute([$class_id]);
                if (!$check->fetch()) {
                    jsonErr("class_id $class_id does not exist in the classes table.", 422);
                }
            } catch (PDOException $e) {
                error_log("[questions_api] Could not verify class_id: " . $e->getMessage());
                // Continue — don't block saving just because classes table check failed
            }
        }

        $stmt = $db->prepare("
            INSERT INTO custom_questions
                (class_id, question, correct_answer, wrong_answer_1, wrong_answer_2, wrong_answer_3, category)
            VALUES
                (:class_id, :question, :correct_answer, :wrong_answer_1, :wrong_answer_2, :wrong_answer_3, :category)
        ");
        $stmt->execute([
            ":class_id"       => $class_id,
            ":question"       => $question,
            ":correct_answer" => $correct_answer,
            ":wrong_answer_1" => $wrong_answer_1,
            ":wrong_answer_2" => $wrong_answer_2,
            ":wrong_answer_3" => $wrong_answer_3,
            ":category"       => $category,
        ]);

        $newId = (int) $db->lastInsertId();

        jsonOk([
            "question" => [
                "id"            => $newId,
                "class_id"      => $class_id,
                "question"      => $question,
                "correct_answer"=> $correct_answer,
                "wrong_answer_1"=> $wrong_answer_1,
                "wrong_answer_2"=> $wrong_answer_2,
                "wrong_answer_3"=> $wrong_answer_3,
                "category"      => $category,
                "created_at"    => date("Y-m-d H:i:s"),
            ]
        ], 201);
    }

    // ── DELETE ───────────────────────────────────────────────────────────────
    if ($method === "DELETE") {
        $id = isset($_GET["id"]) ? (int) $_GET["id"] : 0;
        if ($id <= 0) jsonErr("Valid id query parameter required.", 400);

        $stmt = $db->prepare("DELETE FROM custom_questions WHERE id = ?");
        $stmt->execute([$id]);

        if ($stmt->rowCount() === 0) jsonErr("Question not found.", 404);
        jsonOk(["deleted" => $id]);
    }

    jsonErr("Method not allowed.", 405);

} catch (PDOException $e) {
    $code    = $e->getCode();
    $message = $e->getMessage();
    error_log("[questions_api] PDOException ($code): $message");

    $hint = match(true) {
        str_contains($message, "Access denied")      => "Wrong DB_USER or DB_PASS in questions_api.php.",
        str_contains($message, "Unknown database")   => "Database '" . DB_NAME . "' does not exist. Create it in phpMyAdmin first.",
        str_contains($message, "Connection refused") => "MySQL is not running, or DB_HOST is wrong.",
        str_contains($message, "No such file")       => "MySQL socket not found. Check DB_HOST.",
        str_contains($message, "doesn't exist")      => "A required table is missing. Visit questions_api.php?action=setup to diagnose.",
        default                                      => "See server error log for full details.",
    };

    jsonErr("Database error: $hint", 500, DEV_MODE ? ["pdo_message" => $message, "pdo_code" => $code] : []);

} catch (Throwable $e) {
    error_log("[questions_api] Error: " . $e->getMessage());
    jsonErr("Internal server error.", 500, DEV_MODE ? ["message" => $e->getMessage()] : []);
}