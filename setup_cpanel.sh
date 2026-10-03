#!/usr/bin/env bash
set -euo pipefail

CPANEL_USER="$(id -un)"
PRIVATE_DIR="$HOME/cyberpro_data"
PUBLIC_DIR="$HOME/public_html"
CONFIG_FILE="$PUBLIC_DIR/admin.php"

if [[ ! -d "$PUBLIC_DIR" ]]; then
  echo "Could not find $PUBLIC_DIR. Create your cPanel domain document root first." >&2
  exit 1
fi
if [[ -e "$CONFIG_FILE" ]]; then
  echo "$CONFIG_FILE already exists; leaving it unchanged." >&2
  exit 1
fi

mkdir -p "$PRIVATE_DIR/uploads"
chmod 700 "$PRIVATE_DIR" "$PRIVATE_DIR/uploads"
SECRET="$(php -r 'echo bin2hex(random_bytes(32));')"
cat > "$CONFIG_FILE" <<PHP
<?php
putenv('SECRET_KEY=$SECRET');
putenv('SQLITE_PATH=$PRIVATE_DIR/cyberpro.db');
putenv('MEDIA_DIR=$PRIVATE_DIR/uploads');
PHP
chmod 600 "$CONFIG_FILE"
echo "Created private data directory and protected runtime configuration for $CPANEL_USER."
echo "Now run: php $HOME/cyberpro_backend/create_admin.php"
