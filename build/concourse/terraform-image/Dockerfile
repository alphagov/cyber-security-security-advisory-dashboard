FROM amazonlinux:latest
RUN yum update -y && \
yum install -y python3 python3-pip python3-devel git make zip libffi-devel openssl-devel
COPY $PWD/requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install tox
