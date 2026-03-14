<?php
session_start();
session_destroy();
header("Location: login.html", true, 302);
exit;
?>