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

## Docker Desktop GUI

If you want Docker Desktop for visual container management on Ubuntu, run:

```bash
./scripts/install-docker-desktop-ubuntu.sh
```

Then log out and back in, open Docker Desktop from the application menu, and
accept the Docker Desktop terms. Docker Desktop uses a separate Docker context
named `desktop-linux`; use `docker context ls` to switch between Docker Desktop
and the system Docker Engine.

Check readiness:

```bash
./scripts/docker-desktop-doctor.sh
```

Start this project in Docker Desktop:

```bash
./scripts/docker-desktop-up.sh
```

The containers will appear in Docker Desktop after the first build finishes.
Open the app at `http://localhost:5173`.

Docker Desktop uses a named volume for backend data, so it does not require
sharing the `/data/...` project path in Docker Desktop File Sharing.

Stop the Docker Desktop stack:

```bash
./scripts/docker-desktop-down.sh
```

When Docker Desktop is open, avoid running the same Compose app in the system
Docker Engine at the same time because both can try to bind ports `5173` and
`8000`.

To use Gemini in the Docker image instead of the mock provider:

```bash
GEMINI_API_KEY=your_key docker compose -f docker-compose.yml -f docker-compose.gemini.yml up --build
```

For reproducible Docker Desktop installer downloads, pass a checksum:

```bash
DOCKER_DESKTOP_DEB_SHA256=expected_sha256 ./scripts/install-docker-desktop-ubuntu.sh
```
