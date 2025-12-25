#!/bin/env bash

docker images --format '{{.Repository}}' | grep -q 'gatling'\
    || docker build -t 'gatling' "$RINHA_BENCHMARKS"

# Guarantee fresh start:
curl 'http://localhost:9999/health' >/dev/null 2>&1 \
    && docker compose --progress 'quiet' down

docker compose --progress 'quiet' up -d \
    && docker run --rm \
        --name 'gatling' \
        --network 'host' \
        -v "${RINHA_BENCHMARKS}/results:/opt/gatling/results" \
        gatling >/dev/null \
    && curl 'http://localhost:9999/users-count' \
    && echo

docker compose --progress 'quiet' down
