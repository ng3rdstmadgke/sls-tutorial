# 参考

- [Tutorial | Serverless Framework](https://www.serverless.com/framework/docs/tutorial)
- [FastAPI](https://fastapi.tiangolo.com/)

# サーバーレスフレームワークのインストール

```bash
# pythonのバージョン確認
$ python --version
Python 3.12.2

# nodejsのバージョン確認
$ node --version
v20.11.1

# インストール
$ sudo npm install -g serverless

# slsコマンドが利用できるか確認
$ sls -v
Framework Core: 3.38.0
Plugin: 7.2.3
SDK: 4.5.1
```


# プロジェクト作成

```bash
# 任意のプロジェクト名
PROJECT_NAME=sls-tutorial-app

# --template: AWSをプロバイダとしてPython3でプロジェクトを作成する場合は aws-python3 を指定
# --name: 命名規則は ^[a-zA-Z][0-9a-zA-Z-]+$
# --path: プロジェクトを作成するパスを指定します。
$ sls create --template aws-python3 --name $PROJECT_NAME --path $PROJECT_NAME

# プロジェクトにcd
$ cd $PROJECT_NAME
```

# アプリ実装

## requirements.txtの作成

```bash
$ cat <<EOF > requirements.txt
fastapi[all]~=0.110.0
PyMySQL~=1.1.0
SQLAlchemy~=2.0.27
mangum~=0.17.0
boto3~=1.34.54
EOF

# venv
python -m venv .venv
source .venv/bin/activate

# requirements.txt のインストール
$ pip install -r requirements.txt
```

## アプリの実装

```bash
rm -f handler.py
touch main.py  # serverless.ymlのfunctions.api.handlerに指定したファイル

# lambda関数にインクルードされるファイルを作成
mkdir src static
touch src/env.py static/index.html
```

`${PROJECT_NAME}/main.py`

```py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from src.env import get_env

app = FastAPI(
    redoc_url="/api/redoc",
    docs_url="/api/docs",
    openapi_url="/api/docs/openapi.json",
    root_path=get_env().api_gateway_base_path,
)
allow_origins = ["*"]


@app.get("/api/hello")
def hello():
    env = get_env()
    return {"hoge": env.api_gateway_base_path}

app.mount("/", StaticFiles(directory=f"./static", html=True), name="static")

handler = Mangum(app)
```

`${PROJECT_NAME}/src/env.py`

```py
from functools import lru_cache
from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    api_gateway_base_path: str = "/dev"

@lru_cache
def get_env() -> Environment:
    return Environment()
```

`${PROJECT_NAME}/static/index.html`

```html

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>
  <h1>Hello World</h1>
</body>
</html>
```

## 起動してみる

```bash
uvicorn main:app --reload --port 8080

# localhost:8080をポートフォワードして以下のURLにアクセス
# - http://localhost:8080/
# - http://localhost:8080/api/docs

```

# Serverless Frameworkの設定

## Serverless Python Requirements プラグインの追加

- [Serverless Python Requirements | Serverlessframework](https://www.serverless.com/plugins/serverless-python-requirements)


`serverless-python-requirements` はrequirements.txt で指定したライブラリをLambdaにバンドルすることができます。

```bash
# インストール
$ sls plugin install -n serverless-python-requirements
```

`serverless.yml` の `plugins` にインストールしたプラグインを設定し、pythonライブラリのビルドをコンテナで行うオプション ( `dockerizePip: true` )と、ライブラリをレイヤーとしてデプロイする設定 ( `layer: true` ) を設定します。

`${PROJECT_NAME}/serverless.yml`

```yml

# ... 略 ...
custom:
  pythonRequirements:  # requirements.txt に記載したpythonライブラリをビルドする設定
    dockerImage: public.ecr.aws/lambda/python:3.12  # pythonライブラリのインストールを行うdockerイメージを指定
    layer: true  # pythonライブラリをレイヤーとしてデプロイする設定
plugins:
  - serverless-python-requirements
```

## serverless.yml の設定

サービス名を任意の名前に変更します。

`${PROJECT_NAME}/serverless.yml`

```yml
service: sls-tutorial-app
```


`package` にはlambdaパッケージに含めるファイルをパターンで定義します。

- [Package | ServerlessFramework](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#package)

`${PROJECT_NAME}/serverless.yml`

```yml
package:
  patterns:
    - '!**' # すべてのファイルをexclude
    - 'static/**'  # staticディレクトリは以下をinclude
    - 'src/**'     # srcディレクトリは以下をinclude
    - 'main.py' # main.pyをinclude
```

`resources` の配下にはCloudFormationを記述できます。  
lambdaに適用するロールを `resources` 配下に定義します。  

- [AWS Resources | ServerlessFramework](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#aws-resources)


`${PROJECT_NAME}/serverless.yml`

```yml
resources:
  Resources:
    AppRole: # ManagedPolicyArnsとPoliciesを両方利用した例
      Type: AWS::IAM::Role
      Properties:
        RoleName: SlsTutorial-AppRole
        AssumeRolePolicyDocument:
          Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Action:
                - sts:AssumeRole
              Principal:
                Service:
                  - lambda.amazonaws.com
        ManagedPolicyArns:
          - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
        Policies:
          - PolicyName: ApiServerPolicy
            PolicyDocument:
              Version: "2012-10-17"
              Statement:
                - Resource: "*"
                  Effect: Allow
                  Action:
                    - "s3:*"
                - Resource: "*"
                  Effect: Allow
                  Action:
                    - "dynamodb:*"
                    - "dax:*"
```

`functions` にlambda関数の設定を記述します。

- [AWS Lambda Functions | ServerlessFramework](https://www.serverless.com/framework/docs/providers/aws/guide/functions)

今回はAPIGatewayを利用してAPIサーバーとしてlambdaを利用するので、EventにはAPIGatewayの設定を記述します。  
APIGatewayの設定方法は `HTTP API` と `REST API` の2種類が用意されていますが、今回は `REST API` を利用します。  
※ [REST APIとHTTP APIの違い](https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/http-api-vs-rest.html)

- [HTTP API (API Gateway v2)](https://www.serverless.com/framework/docs/providers/aws/events/http-api)
- [REST API (API Gateway v1)](https://www.serverless.com/framework/docs/providers/aws/events/apigateway)


`${PROJECT_NAME}/serverless.yml`

```yml
functions:
  api:
    handler: main.handler  # main.pyのhandlerをハンドラとして利用する
    timeout: 30
    role: AppRole  # resources配下に実装したロール名
    events:
      # すべてのメソッド・リクエストを受け取る
      - http:
          path: /
          method: ANY
          cors: true  # CORSを許可する
      - http:
          path: /{path+}
          method: ANY
          cors: true
    environment:  # 環境変数の定義
      API_GATEWAY_BASE_PATH: "/${self:provider.stage}"  # provider.stage の値を利用
    layers:
      # serverless-python-requirementsプラグインで作成したLayerを利用する設定を記述
      # https://www.serverless.com/plugins/serverless-python-requirements#lambda-layer
      - Ref: PythonRequirementsLambdaLayer
```

`provider` にawsの設定を記述しましょう

- [Provider | ServerlessFramework](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#provider)
  - [API Gateway v1 REST APIの設定](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#api-gateway-v2-http-api)
  - [API Gateway v2 HTTP APIの設定](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#api-gateway-v1-rest-api)

`provider.deploymentBucket.name` には自身で用意したs3バケット名を指定してください。

`${PROJECT_NAME}/serverless.yml`

```yml
provider:
  name: aws
  runtime: python3.12
  stage: ${opt:stage, "dev"}  # ステージ名 (--stageオプションがなければdev)
  region: "ap-northeast-1"  # デプロイするリージョン
  deploymentBucket:
    name: "sls-deploy-gcappr58"  # デプロイアーティファクトを保存するs3バケット
  apiGateway:  # API Gateway v1 REST APIの設定
    # バイナリファイルを返却できるようにする設定
    binaryMediaTypes:
      - '*/*'
```



# デプロイ

```bash
# デプロイ
sls deploy --stage prd

# デプロイしたAPIにアクセス
# - https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/
# - https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/api/docs

# 削除
sls remove --stage prd
```
