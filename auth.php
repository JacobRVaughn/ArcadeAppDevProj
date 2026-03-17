<?php
include 'authService.php';
session_start();
header('Content-Type: application/json');

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

            // Return redirect URL based on role
            if ($result['role'] === 'teacher') {
                $redirect = 'teacherdashboard.html';
            } elseif ($result['role'] === 'admin') {
                $redirect = 'admin_dashboard.php';
            } else {
                $redirect = 'student-dashboard.php';
            }

            echo json_encode([
                'status'   => 'success',
                'message'  => 'Welcome back, ' . htmlspecialchars($result['username']) . '!',
                'redirect' => $redirect
            ]);

        } else {
            echo json_encode([
                'status'  => 'error',
                'message' => $result['message'] ?? 'Invalid email or password. Please try again.'
            ]);
        }
        exit;

    } elseif (isset($_POST['signup_submit'])) {
        $signup_username = trim($_POST["signup_username"]);
        $signup_email    = trim($_POST["signup_email"]);
        $signup_password = trim($_POST["signup_password"]);
        $signup_confirm  = trim($_POST["signup_confirm"]);
        $role            = $_POST["role"];

        if ($signup_password !== $signup_confirm) {
            echo json_encode([
                'status'  => 'error',
                'message' => 'Passwords do not match. Please try again.'
            ]);
            exit;
        }

        $result = signupUser($signup_username, $signup_email, $signup_password, $role);

        if ($result === 'success') {
            // Log the user in immediately after signup
            $loginResult = loginUser($signup_email, $signup_password);

            if ($loginResult['status'] === 'success') {
                $_SESSION['username']  = $loginResult['username'];
                $_SESSION['user_id']   = $loginResult['id'];
                $_SESSION['role']      = $loginResult['role'];
                $_SESSION['logged_in'] = true;

                if ($loginResult['role'] === 'teacher') {
                    $redirect = 'teacherdashboard.html';
                } elseif ($loginResult['role'] === 'admin') {
                    $redirect = 'admin_dashboard.php';
                } else {
                    $redirect = 'student-dashboard.php';
                }

                echo json_encode([
                    'status'   => 'success',
                    'message'  => 'Account created! Welcome, ' . htmlspecialchars($loginResult['username']) . '!',
                    'redirect' => $redirect
                ]);
            } else {
                // Signup worked but auto-login failed, send to login page
                echo json_encode([
                    'status'   => 'success',
                    'message'  => 'Account created successfully! Please sign in.',
                    'redirect' => null
                ]);
            }
        } else {
            echo json_encode([
                'status'  => 'error',
                'message' => $result ?? 'Sign up failed. Please try again.'
            ]);
        }
        exit;
    }
}
?>