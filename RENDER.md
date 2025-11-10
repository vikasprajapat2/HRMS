# Deploying backend to Render

This project is configured to deploy the Flask backend to Render using the included `Dockerfile`.

Quick steps

1. Create a Render account and connect your GitHub repository.

2. Create a new Web Service:
   - Click "New" → "Web Service"
   - Connect the `vikasprajapat2/HRMS` repository and select the `main` branch
   - For Environment choose: "Docker"
   - For Dockerfile Path use: `./Dockerfile`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
   - Plan: choose the plan you want (free or paid)

3. Add Environment Variables (Render Dashboard → Environment)
   - SECRET_KEY: a secure random string
   - MYSQL_HOST
   - MYSQL_PORT (3306)
   - MYSQL_DATABASE
   - MYSQL_USER
   - MYSQL_PASSWORD

4. Deploy
   - Render will build the Docker image using the `Dockerfile` in the repo and deploy the service.

5. Run database migrations
   - Open the Render shell for the service (Dashboard → Instances → Shell)
   - Run:
     ```bash
     export FLASK_APP=app.py
     flask db migrate -m "Initial"
     flask db upgrade
     ```

Notes and recommendations
- Use managed MySQL (Render offers managed databases or you can connect an external DB).
- Do not use SQLite in production on Render; use the MySQL env variables above.
- If Render provides a single `DATABASE_URL`, you can either parse it into components inside the app or paste individual `MYSQL_*` env vars in the Render UI.
- If you prefer not to use Docker, Render also supports direct Python services with build commands — but the Docker route is the most predictable since we added a `Dockerfile`.

If you'd like, I can also:
- Add a small script to run migrations automatically during deploy
- Add parsing logic to support a single `DATABASE_URL` env var
- Create a `render.yaml` for Infrastructure as Code (optional)
