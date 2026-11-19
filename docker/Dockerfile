FROM python:3.13-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /benchmark
COPY src/ ./src/
ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python", "-m", "src"]
