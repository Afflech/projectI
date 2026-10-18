# Docker Setup

Use Docker Compose to run the backend and frontend together without opening two
terminal sessions.

## Start

If Docker is not installed on Ubuntu, run this once in a normal terminal so you
can enter your sudo password:

```bash
./scripts/install-docker-ubuntu.sh
```

Then start the app with the helper. It preserves file ownership for
`backend/data/` on Linux:

```bash
./scripts/docker-up.sh
```

You can also call Docker Compose directly:

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:5173`
- Backend health check: `http://localhost:8000/health`

The backend stores SQLite data, uploads, and vectors in `backend/data/`.

## Stop

```bash
./scripts/docker-down.sh
```

## Optional Gemini Key

The Docker image is optimized for the offline demo path: it uses the mock LLM
provider by default and the NumPy vector-search fallback. This keeps first-time
container builds much faster than installing FAISS and the Gemini SDK.

To test Gemini inside Docker, add `google-generativeai` to
`backend/requirements.docker.txt`, rebuild, and pass the API key:

```bash
GEMINI_API_KEY=your_key docker compose up --build
```

## Common Cases

If port `5173` or `8000` is already in use, stop the process using that port or
change the left side of the port mapping in `docker-compose.yml`.

If dependencies change, rebuild:

```bash
docker compose build --no-cache
```

## Notes

After installing Docker, Linux may require logging out and back in before your
user can run Docker without `sudo`.
