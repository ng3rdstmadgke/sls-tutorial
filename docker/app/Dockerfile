FROM public.ecr.aws/lambda/python:3.11

ARG PROJECT_NAME
ENV PATH $PATH:/usr/sbin

RUN mkdir -p /opt/app
WORKDIR /opt/app

# pip install
COPY ${PROJECT_NAME}/requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY ${PROJECT_NAME} /opt/app/api

# importの起点となるパスを環境変数として定義
ENV PYTHONPATH=/opt/app/api

ENTRYPOINT []

CMD ["uvicorn", "main:app", "--reload", "--port", "8080"]