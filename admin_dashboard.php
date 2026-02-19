<?php
session_start();
$conn = new mysqli("localhost", "root", "", "arcade_db");

// 🔒 Only allow admin
// if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
//     header("Location: index.html");
//     exit();
// }

// Handle Update Submission
if (isset($_POST['update_user'])) {
    $id = $_POST['user_id'];
    $username = $_POST['username'];
    $email = $_POST['email'];
    $role = $_POST['role'];
    $xp = isset($_POST['xp']) ? intval($_POST['xp']) : 0;

    $stmt = $conn->prepare("UPDATE users SET username=?, email=?, role=?, xp=? WHERE id=?");
    $stmt->bind_param("sssii", $username, $email, $role, $xp, $id);
    $stmt->execute();
}

// Fetch all users
$result = $conn->query("SELECT id, username, email, role, xp FROM users");
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard | EDUQuest Arcade</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<div class="auth-container">

    <!-- Background Blur Effects -->
    <div class="background-blur"></div>
    <div class="background-blur-bottom"></div>

    <div class="auth-box leaderboard-auth-box" style="max-width: 1000px; width:100%;">

        <!-- Header -->
        <div class="leaderboard-header">
            <div class="leaderboard-title">
                <div class="leaderboard-star">A</div>
                <div>
                    <h1>Admin Dashboard</h1>
                    <p>Manage EDUQuest Arcade Users</p>
                </div>
            </div>
        </div>

        <!-- Users Table -->
        <div style="overflow-x:auto;">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>XP</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($user = $result->fetch_assoc()): ?>
                    <tr>
                        <form method="POST" action="admin_dashboard.php">
                            <input type="hidden" name="user_id" value="<?= $user['id'] ?>">
                            <td><?= $user['id'] ?></td>

                            <td>
                                <input type="text" name="username" value="<?= htmlspecialchars($user['username']) ?>">
                            </td>

                            <td>
                                <input type="email" name="email" value="<?= htmlspecialchars($user['email']) ?>">
                            </td>

                            <td>
                                <select name="role" class="role-select">
                                    <option value="student" <?= $user['role'] == 'student' ? 'selected' : '' ?>>Student</option>
                                    <option value="teacher" <?= $user['role'] == 'teacher' ? 'selected' : '' ?>>Teacher</option>
                                    <option value="admin" <?= $user['role'] == 'admin' ? 'selected' : '' ?>>Admin</option>
                                </select>
                            </td>

                            <td>
                                <input type="number" name="xp" value="<?= $user['xp'] ?? 0 ?>">
                            </td>

                            <td>
                                <button type="submit" name="update_user" class="submit-btn" style="padding:0.5rem 1rem;">Save</button>
                            </td>
                        </form>
                    </tr>
                    <?php endwhile; ?>
                </tbody>
            </table>
        </div>

    </div>
</div>

</body>
</html>
