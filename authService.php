<?php
$conn = new mysqli("localhost", "root", "", "arcade_db");

// Called from auth.php to verify login information in the database
function loginUser($email, $password) {
    try {
        global $conn;

        $stmt = $conn->prepare("SELECT password FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        $row = $result->fetch_assoc();

        if (!isset($row) || empty($row)) {
            return 'no user matches';
        }

        if (password_verify($password, $row['password'])) {
            return 'success';
        } else {
            return 'failure pass does not match';
        }

    } catch (Exception $e) {
        error_log($e->getMessage());
    }
}

//Create db user table entry for a new user
function signupUser($username,$email,$password,$role) {
    global $conn;

    if (checkExistingAcc($email, $username)) {
        return 'account for username or email already exist';
    }

    $hashedPass = password_hash($password, PASSWORD_DEFAULT);

    $stmt = $conn->prepare("INSERT INTO users (username, password, email, role) VALUES (?,?,?,?)");
    $stmt->bind_param("ssss", $username, $hashedPass, $email, $role);
    $stmt->execute();

    if ($stmt->affected_rows > 0) {
        return 'success';
    } else {
        return 'sql error has occured';
    }
    
}

// Each account needs a unique username and email no duplicates 
// we check in the users table for any duplicate entries
// returns true if there is an existing account
function checkExistingAcc($email, $username) {
    global $conn;

    $stmt = $conn->prepare("SELECT * FROM users WHERE username = ? OR email = ?");
    $stmt->bind_param("ss", $username, $email);
    $stmt->execute();

    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        return true;
    } else {
        return false;
    }

}


?>