# ResumeIQ Deployment

This project is a Flask app with MySQL storage, a scikit-learn KNN model, and OpenRouter/OpenAI-compatible AI calls.

## Local Setup

1. Create and activate a virtual environment.

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Create a local `.env` file from `.env.example`, then fill in your real values. Do not commit `.env`.

4. Import the database schema into MySQL.

   ```bash
   mysql --host=YOUR_HOST --port=YOUR_PORT --user=YOUR_USER --password YOUR_DATABASE < database/schema.sql
   ```

5. Run locally.

   ```bash
   python app.py
   ```

   Open `http://127.0.0.1:5000`.

## Required Environment Variables

Set these locally in `.env` and on Render:

- `SECRET_KEY`: A long random secret for Flask sessions.
- `MYSQL_HOST`: Cloud MySQL host.
- `MYSQL_PORT`: Cloud MySQL port, usually `3306` or the provider's custom port.
- `MYSQL_USER`: Cloud MySQL username.
- `MYSQL_PASSWORD`: Cloud MySQL password.
- `MYSQL_DATABASE`: Database name.
- `OPENAI_API_KEY`: Your OpenRouter API key.
- `OPENAI_BASE_URL`: `https://openrouter.ai/api/v1`
- `OPENAI_MODEL`: The OpenRouter model name, for example `openai/gpt-4o-mini`.

Optional:

- `MYSQL_CONNECT_TIMEOUT`: Defaults to `10`.
- `MYSQL_SSL_CA`: Path to a CA certificate file if your MySQL provider requires one.

## Free Database

Aiven currently offers an always-free Aiven for MySQL plan with 1 GB storage, 1 GB RAM, and no credit card requirement. It is suitable for a small demo or portfolio deployment, not heavy production traffic.

Suggested setup:

1. Create an Aiven account.
2. Create a new MySQL service on the Free plan.
3. Wait until the service status is running.
4. Open the service overview and copy the host, port, user, password, and database name.
5. Import `database/schema.sql` into that database using MySQL Workbench, DBeaver, the Aiven web console if available, or the `mysql` CLI.

## Render Web Service

Create a Render Web Service from your GitHub repository.

Use these values:

- Language: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Instance Type: `Free`

Add all required environment variables in Render before deploying.

Render free web services can spin down after inactivity and restart later, which means the first request after idle time can be slow. Free web services also do not include persistent disks, but this app stores user data in MySQL and only uses browser printing for PDFs, so no persistent local disk is required.

## Known Notes

- `models/resume_knn_model.pkl` is loaded from a project-relative path and must stay in the repository.
- `ML/knn_model.json` is loaded from a project-relative path for model metadata and must stay in the repository.
- The app uses MySQL and has not been converted to PostgreSQL.
- The application is served by Gunicorn on Render; `python app.py` is only for local development.
