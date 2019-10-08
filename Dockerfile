FROM python:3
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y zip

# Install python deps
COPY requirements-dev.txt .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1

COPY . .
