FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add npm

COPY . .

WORKDIR /usr/src/app/build

RUN npm install -g gulp-cli
RUN npm install
RUN npm rebuild node-sass
RUN gulp

WORKDIR /usr/src/app