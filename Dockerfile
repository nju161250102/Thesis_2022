FROM ubuntu:latest

RUN apt update \
    && apt install -y tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && apt install -y openjdk-8-jdk git python3 python3-pip wget unzip \
    && pip3 install numpy pandas requests wget jira pydriller \
    && apt purge -y --auto-remove \
    && export GIT_PYTHON_REFRESH=quiet
