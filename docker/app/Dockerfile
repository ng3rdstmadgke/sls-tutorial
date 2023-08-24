FROM public.ecr.aws/lambda/python:3.9

ENV PATH $PATH:/usr/sbin

# update package
RUN yum update -y && \
    yum install -y locales gcc unzip jq curl shadow-utils vim tmux sudo wget && \
    yum install -y iputils-ping net-tools less groff

# set timezone
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# install awscli
RUN cd /tmp && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.0.30.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -r aws awscliv2.zip

RUN mkdir -p /opt/app
WORKDIR /opt/app

# pip install
COPY sample-app/requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY sample-app /opt/app/api

# importの起点となるパスを環境変数として定義
ENV PYTHONPATH=/opt/app/api

ENTRYPOINT []

CMD ["uvicorn", "main:app", "--reload", "--port", "8080"]
