# Deploying backend to Railway

This project is intended to run the Flask backend on Railway (or similar PaaS) and the frontend on Vercel.

Follow these steps to deploy the backend on Railway:

1. Create a Railway project and link your GitHub repository.

2. Add environment variables in Railway (Project > Settings > Variables). At minimum configure:

- SECRET_KEY: a secure random string
- MYSQL_HOST: the host provided by Railway (or your managed MySQL)
- MYSQL_PORT: usually 3306
- MYSQL_DATABASE: database name
- MYSQL_USER: DB username
- MYSQL_PASSWORD: DB password

Railway also exposes a single `DATABASE_URL` for some add-ons. This project expects the individual MySQL variables above — you can parse `DATABASE_URL` to set them or use Railway's UI to set each variable.

3. Ensure `requirements.txt` includes `gunicorn` (it should already). Railway will install dependencies automatically.

4. The repo contains a `Procfile` with the command:

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

This tells Railway how to run the Flask WSGI app.

5. Database migrations:

- On the Railway shell (or locally with proper env vars set), run:

```bash
# set FLASK_APP if needed
$env:FLASK_APP = 'app.py'
flask db migrate -m "Deploy migration"
flask db upgrade
```

6. Filesystem notes:

- Do NOT rely on SQLite or local file storage for production on Railway. Use a managed MySQL instance and set the environment variables above.
- If your app stores uploads in `static/uploads`, configure an external storage (S3-compatible) or ensure Railway persistent storage is adequate for your needs.

7. Frontend on Vercel

- Deploy the frontend (any static site or Next.js app) on Vercel.
- Configure the frontend to call the backend API URL provided by Railway (set it in Vercel Environment variables if needed).

8. Optional: Docker

If you prefer Docker, add a `Dockerfile` and configure Railway to build the container image.

---

If you want, I can also:
- Add a `Dockerfile` for containerized deployment
- Add a small `deploy/` script to run migrations automatically on deploy
- Parse `DATABASE_URL` into individual env vars if Railway only exposes a single URL

Tell me which extras you want and I'll add them and push to the repo.