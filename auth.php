<?php 

include 'authService.php';

session_start();

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // Login Post Form
    if (isset($_POST['login_submit']) && isset($_POST["login_email"]) && isset($_POST["login_password"]) 
    ) {

    $email = trim($_POST["login_email"]);
    $password = trim($_POST["login_password"]);

    $result = loginUser($email,$password);

    if ($result == 'success') {

        $_SESSION['username'] = $username;
        $_SESSION['logged_in'] = true;

        header("Location: http://localhost/my_arcade_game/studentDashboard.html", true, 302);
        // always follow header with exit
        exit;

    } else {
        echo $result;
    }

    } 
    // Signup Post Form
    elseif (isset($_POST['signup_submit']) && isset($_POST["signup_username"]) 
        && isset($_POST["signup_email"]) && isset($_POST["signup_password"]) && isset($_POST["signup_confirm"])
    ) {

        $signup_username = trim($_POST["signup_username"]);
        $signup_email = trim($_POST["signup_email"]);
        $signup_password = trim($_POST["signup_password"]);
        $signup_confirm = trim($_POST["signup_confirm"]);

        if ($signup_password != $signup_confirm) {
            return "passwords do not match";
        }

        $result = signupUser($signup_username, $signup_email, $signup_password);

        if ($result == 'success') {
            $_SESSION['username'] = $signup_username;
            $_SESSION['logged_in'] = true;

            header("Location: http://localhost/my_arcade_game/studentDashboard.html", true, 302);
            // always follow header with exit
            exit;
        } else {
            echo $result;
        }

    }

}

?>