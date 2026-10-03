# PHP backend deployment

This API replaces the FastAPI application and supports PHP 8.1+ with PDO SQLite or PDO MySQL. The React frontend keeps using the same `/api/...` paths.

## cPanel setup

1. In cPanel, select PHP 8.1 or newer and enable `pdo_sqlite` for SQLite or `pdo_mysql` for MySQL/MariaDB. Also enable `fileinfo` for image uploads. The documented SQLite admin commands require the PHP CLI to include the same PDO driver.
2. Build the frontend locally from `CyberPro_Website_Frontend` with `npm run build`, then deploy that folder using the repo's cPanel deployment. Its `.cpanel.yml` copies `dist` plus the PHP front controller and rewrite rules into `public_html`.
3. Deploy `cyberpro_backend` using its `.cpanel.yml`; this places `create_admin.php` in `~/cyberpro_backend` and creates the private data/upload directories.
4. Set these environment variables in the hosting control panel where available. Where cPanel does not expose per-application environment settings, copy `admin.example.php` to `public_html/admin.php`, replace the placeholder values, and ensure it stays blocked by `.htaccess`:

   - `SECRET_KEY`: a private random value, at least 32 characters.
   - `SQLITE_PATH`: `/home/CPANEL_USER/cyberpro_data/cyberpro.db` (recommended for the default SQLite database).
   - For MySQL/MariaDB: `DATABASE_DSN=mysql:host=localhost;dbname=YOUR_DB;charset=utf8mb4`, `DATABASE_USER`, and `DATABASE_PASSWORD`.
   - Optional: `SQLITE_PATH` for a SQLite database path outside the public document root.
   - Optional: `MEDIA_DIR` (recommended: `/home/CPANEL_USER/cyberpro_data/uploads`) for a writable uploads directory outside the public document root, and `MEDIA_BASE_URL` if the API is hosted on a separate subdomain.

   With no database variables, the API creates `data/cyberpro.db` beside `index.php` with owner-only file permissions; set `SQLITE_PATH` to keep that writable data outside `public_html`.

   From cPanel Terminal, run `bash ~/cyberpro_backend/setup_cpanel.sh`. It generates a strong secret, creates private database/upload directories, and writes `public_html/admin.php` with restrictive permissions. Do not run it if `public_html/admin.php` already exists.

5. Create the first admin user from cPanel Terminal. It accepts an email and password interactively and stores a PHP password hash:

   ```sh
   php ~/cyberpro_backend/create_admin.php
   ```

6. Point the frontend's `VITE_API_URL` to the API origin if it is on another domain. For same-domain deployment, leave it unset. Rebuild the frontend and deploy its `dist` directory to `public_html`.

7. Confirm the API responds by opening `https://YOUR_DOMAIN/health`; it should return `{"status":"ok"}`. Then open the website and try `/admin` with the administrator account.

The PHP API also verifies the existing Python PBKDF2 admin hash format and accepts the same `SECRET_KEY` JWT signature, so an existing database and secret can be reused if available. The new admin helper writes standard PHP password hashes.

## Local development

```sh
cd cyberpro_backend
SECRET_KEY='local-development-secret-change-this' php -S 127.0.0.1:8000 index.php
```

Set `VITE_API_URL=http://127.0.0.1:8000` for a frontend development build/server that needs to call the local API.
