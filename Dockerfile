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
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /src folder as a directory where the source code is stored.
WORKDIR /src

# Copy the source code of the project into the container.
COPY . /src

CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]

# docker build -t wlili . && docker run \
#   -p 8002:8002 \
#   --mount type=bind,source="$PWD/db.sqlite3",target=/src/db.sqlite3 \
#   -it wlili
