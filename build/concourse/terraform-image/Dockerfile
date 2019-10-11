FROM amazonlinux:latest
RUN yum update -y && \
yum install -y python3 python3-pip python3-devel git make zip libffi-devel openssl-devel
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install tox
COPY $PWD/requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
RUN sleep 300
COPY build/concourse/sts-assume-role.sh /usr/local/bin/sts-assume-role.sh
