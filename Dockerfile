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
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Use /src folder as a directory where the source code is stored.
WORKDIR /src

ENV DJANGO_SETTINGS_MODULE="wlili.settings.production"

COPY src/ /src

RUN DJANGO_SECRET_KEY=placeholder DJANGO_ALLOWED_HOST=localhost DJANGO_DB_PATH=/dev/null python manage.py collectstatic --noinput

RUN adduser --uid 1234 vv
USER vv

CMD ["gunicorn", "--bind", ":8888", "-w", "2", "--timeout", "120", "--max-requests", "500", "--max-requests-jitter", "50", "wlili.wsgi:application"]
