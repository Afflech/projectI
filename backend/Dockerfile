FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ARG INSTALL_GEMINI=false

COPY requirements.docker.txt .
COPY requirements.gemini.txt .
RUN pip install -r requirements.docker.txt \
    && if [ "$INSTALL_GEMINI" = "true" ]; then pip install -r requirements.gemini.txt; fi

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
