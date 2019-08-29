FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt install -y npm

COPY . .

WORKDIR /usr/src/app/build

RUN npm install -g gulp-cli

WORKDIR /usr/src/app
