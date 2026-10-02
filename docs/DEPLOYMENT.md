# Deployment

SitePulse v1.0 is designed to run locally with SQLite or in production with
PostgreSQL.

## Docker

Build the image:

```bash
docker build -t sitepulse .
```

Run with SQLite:

```bash
docker run --rm -p 8000:8000 sitepulse
```

Then open:

```text
http://127.0.0.1:8000/
```

## Local PostgreSQL stack

Docker Compose starts SitePulse and PostgreSQL together:

```bash
docker compose up --build
```

The dashboard will be available at:

```text
http://127.0.0.1:8000/
```

Stop the stack with:

```bash
docker compose down
```

Use `docker compose down -v` if you intentionally want to remove the local
PostgreSQL data volume.

## Render

The repository includes a `render.yaml` Blueprint that defines:

- a Docker web service
- a Render PostgreSQL database
- the `SITEPULSE_DATABASE_URL` connection between them
- the `/health` health-check endpoint

Render reads the web service's `PORT` environment variable automatically.
SitePulse's Docker command binds Uvicorn to `0.0.0.0` and uses that port.

The production database connection is provided through:

```text
SITEPULSE_DATABASE_URL
```

SitePulse accepts standard `postgresql://` and `postgres://` URLs and
automatically uses the psycopg 3 SQLAlchemy driver.

## Production notes

The current v1.0 schema is created automatically at application startup with
SQLAlchemy metadata. A future release can add Alembic migrations when schema
evolution becomes necessary.
