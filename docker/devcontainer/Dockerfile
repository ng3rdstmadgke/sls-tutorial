# https://hub.docker.com/_/microsoft-devcontainers
# https://hub.docker.com/_/microsoft-devcontainers-python
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ARG http_proxy
ARG https_proxy
ARG no_proxy

ENV http_proxy=$http_proxy \
    https_proxy=$https_proxy \
    no_proxy=$no_proxy \
    HTTP_PROXY=$http_proxy \
    HTTPS_PROXY=$https_proxy \
    NO_PROXY=$no_proxy

RUN apt-get update && \
    apt-get install -y \
      default-mysql-client \
      bash-completion \
      procps \
      net-tools \
      iputils-ping \
      locales \
      make \
      jq \
      fzf \
      vim \
      curl \
      wget \
      git \
      groff \
      less \
      sudo \
      gcc

# ロケール設定
RUN echo 'ja_JP.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# aws cli インストール
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# pip インストール
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip & \
    pip install -r /tmp/requirements.txt

# terraform インストール
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform

# node.js インストール
# https://github.com/nodesource/distributions#installation-instructions
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&\
    apt-get install -y nodejs

# serverless framework インストール
RUN npm install -g serverless