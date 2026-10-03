<?php
declare(strict_types=1);
require_once __DIR__ . '/index.php';

if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
initialize_db();
$username = strtolower(trim((string)readline('Admin email: ')));
if (!filter_var($username, FILTER_VALIDATE_EMAIL) || !str_ends_with($username, '@cyberpro.ke')) { fwrite(STDERR, "Use a valid @cyberpro.ke email address.\n"); exit(1); }
if (!function_exists('read_hidden')) {
    function read_hidden(string $prompt): string {
        fwrite(STDOUT, $prompt);
        if (DIRECTORY_SEPARATOR === '/') { system('stty -echo'); }
        $value = (string)fgets(STDIN);
        if (DIRECTORY_SEPARATOR === '/') { system('stty echo'); fwrite(STDOUT, "\n"); }
        return rtrim($value, "\r\n");
    }
}
$password = read_hidden('Password (12+ characters): ');
$confirm = read_hidden('Confirm password: ');
if (strlen($password) < 12 || !hash_equals($password, $confirm)) { fwrite(STDERR, "Passwords must match and contain at least 12 characters.\n"); exit(1); }
$statement = db()->prepare('SELECT id FROM admin_users WHERE username = ?');
$statement->execute([$username]);
$id = $statement->fetchColumn();
if ($id) { $statement = db()->prepare('UPDATE admin_users SET hashed_password = ? WHERE id = ?'); $statement->execute([password_hash($password, PASSWORD_DEFAULT), $id]); }
else { $statement = db()->prepare('INSERT INTO admin_users(username, hashed_password) VALUES(?, ?)'); $statement->execute([$username, password_hash($password, PASSWORD_DEFAULT)]); }
fwrite(STDOUT, "Administrator account ready: $username\n");
