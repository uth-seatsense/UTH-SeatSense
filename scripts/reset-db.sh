#!/usr/bin/env sh
set -eu
docker compose down --volumes
docker compose up --build -d db
