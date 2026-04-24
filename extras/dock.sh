#!/bin/bash
docker build -t wlili . && \
docker run -p 8003:8003 \
  --mount type=bind,source="$PWD/container.db.sqlite3",target="/home/vv/db.sqlite3" \
  --mount type=bind,source="$PWD/media",target="/src/media" \
  -e DJANGO_SECRET_KEY=sikrit \
  -e DJANGO_ALLOWED_HOST=localhost \
  -e DJANGO_DB_PATH=/home/vv/db.sqlite3 -it wlili
