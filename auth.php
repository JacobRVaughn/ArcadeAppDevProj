<?php
include 'authService.php';
session_start();

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (isset($_POST['login_submit'])) {
        $email    = trim($_POST["login_email"]);
        $password = trim($_POST["login_password"]);

        $result = loginUser($email, $password);

        if ($result['status'] === 'success') {
            $_SESSION['username']  = $result['username'];
            $_SESSION['user_id']   = $result['id'];
            $_SESSION['role']      = $result['role'];
            $_SESSION['logged_in'] = true;

            // Redirect based on role
            if ($result['role'] === 'teacher') {
                header("Location: teacherdashboard.html", true, 302);
            } elseif ($result['role'] === 'admin') {
                header("Location: admin_dashboard.php", true, 302);
            } else {
                header("Location: student-dashboard.php", true, 302);
            }
            exit;
        } else {
            echo $result['status'];
        }

    } elseif (isset($_POST['signup_submit'])) {
        // ...existing code...
        $signup_username = trim($_POST["signup_username"]);
        $signup_email    = trim($_POST["signup_email"]);
        $signup_password = trim($_POST["signup_password"]);
        $signup_confirm  = trim($_POST["signup_confirm"]);
        $role            = $_POST["role"];

        if ($signup_password !== $signup_confirm) {
            echo "passwords do not match";
            exit;
        }

        $result = signupUser($signup_username, $signup_email, $signup_password, $role);

        if ($result === 'success') {
            $conn = new mysqli("localhost", "root", "", "arcade_db");
            $stmt = $conn->prepare("SELECT id FROM users WHERE email = ?");
            $stmt->bind_param("s", $signup_email);
            $stmt->execute();
            $row = $stmt->get_result()->fetch_assoc();

            $_SESSION['username']  = $signup_username;
            $_SESSION['user_id']   = $row['id'] ?? null;
            $_SESSION['role']      = $role;
            $_SESSION['logged_in'] = true;

            // Redirect based on role (same as login)
            if ($role === 'teacher') {
                header("Location: teacherdashboard.html", true, 302);
            } elseif ($role === 'admin') {
                header("Location: admin_dashboard.php", true, 302);
            } else {
                header("Location: student-dashboard.php", true, 302);
            }
            exit;
        } else {
            echo $result;
        }
    }
}
?>