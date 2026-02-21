# Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
FROM python:3.12-slim-bookworm

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install the project requirements.
RUN pip install --upgrade pip
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /src folder as a directory where the source code is stored.
WORKDIR /src

# Copy the source code of the project into the container.
COPY . /src

ENV DJANGO_SETTINGS_MODULE="wlili.settings.production"

RUN DJANGO_SECRET_KEY=placeholder DJANGO_ALLOWED_HOST=localhost DJANGO_DB_PATH=/dev/null python manage.py collectstatic --noinput

RUN adduser --uid 1234 nando
USER nando

CMD ["gunicorn", "--bind", ":8003", "wlili.wsgi:application"]

# docker build -t wlili . && docker run \
#   -p 8003:8003 \
#   --mount type=bind,source="$PWD/container.db.sqlite3",target=/home/nando/db.sqlite3 \
#   -e DJANGO_SECRET_KEY=placeholder \
#   .e DJANGO_ALLOWED_HOST=localhost \
#   .e DJANGO_DB_PATH=/home/nando/db.sqlite3 \
#   -it wlili
