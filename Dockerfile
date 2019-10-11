FROM python:3
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y zip wget

RUN wget https://releases.hashicorp.com/terraform/0.12.10/terraform_0.12.10_linux_amd64.zip &&\
        wget https://releases.hashicorp.com/terraform/0.12.10/terraform_0.12.10_SHA256SUMS &&\
        wget https://releases.hashicorp.com/terraform/0.12.10/terraform_0.12.10_SHA256SUMS.sig &&\
        gpg --version &&\
        gpg --keyserver hkps://keyserver.ubuntu.com --receive-keys 51852D87348FFC4C &&\
        gpg -d terraform_0.12.10_SHA256SUMS.sig &&\
        sha256sum --ignore-missing -c terraform_0.12.10_SHA256SUMS &&\
        unzip terraform_0.12.10_linux_amd64.zip &&\
        chmod 555 terraform &&\
        cp terraform /bin/

# Install python deps
COPY requirements-dev.txt .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
COPY sts-assume-role.sh /usr/local/bin/sts-assume-role.sh

COPY . .
