FROM ruby:2.6.2
RUN apt-get update -y && \
apt-get install -y nodejs
COPY $PWD/Gemfile Gemfile
COPY $PWD/Gemfile.lock Gemfile.lock
RUN bundle install
