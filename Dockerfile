# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# system-level deps (mysqlclient alternative, build tools if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install python deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app

# Flask config
ENV FLASK_APP=app.main:app
# we'll pass DB_HOST, DB_USER, ... from docker-compose

EXPOSE 5000

# run the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
