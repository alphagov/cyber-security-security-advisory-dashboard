FROM python:3
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y npm zip

# Install python deps
COPY requirements-dev.txt .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app/build

# Update node version
RUN npm install -g n
RUN n 10.16.3
RUN npm install -g gulp-cli

# Update node deps
COPY build/package.json .
RUN npm install
RUN npm rebuild node-sass

# Build sass with gulp
COPY build/gulpfile.js .
COPY build/gulp_tasks ./gulp_tasks
COPY build/sass ./sass
RUN gulp

WORKDIR /usr/src/app
COPY . .
