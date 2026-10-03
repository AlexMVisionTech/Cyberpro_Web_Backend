<?php
// Copy to admin.php and replace the values before deploying. Restrict access to
// this file and do not commit the real version; use cPanel environment settings
// when your account provides them.
putenv('SECRET_KEY=replace-with-a-long-random-secret');
putenv('SQLITE_PATH=/home/CPANEL_USER/cyberpro_data/cyberpro.db');
putenv('MEDIA_DIR=/home/CPANEL_USER/cyberpro_data/uploads');
