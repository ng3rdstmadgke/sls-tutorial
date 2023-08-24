# 参考

- [Tutorial | Serverless Framework](https://www.serverless.com/framework/docs/tutorial)
- [FastAPI](https://fastapi.tiangolo.com/)

# node.jsのインストール

```bash
# nvm インストール
# https://github.com/nvm-sh/nvm#installing-and-updating
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash

# v16系のLTSをインストール
nvm install --lts=gallium

# v16系のLTSをデフォルトに設定
nvm alias default lts/gallium

# 確認
nvm list
```

# サーバーレスフレームワークのインストール

```bash
# インストール
npm install -g serverless

# slsコマンドが利用できるか確認
sls -v
```


# プロジェクト作成

```bash
# --template: AWSをプロバイダとしてPython3でプロジェクトを作成する場合は aws-python3 を指定
# --name: 命名規則は ^[a-zA-Z][0-9a-zA-Z-]+$
# --path: プロジェクトを作成するパスを指定します。
sls create --template aws-python3 --name sample-app --path sample-app

# プロジェクトにcd
cd sample-app
```

## Serverless Python Requirements プラグインの追加

- [Serverless Python Requirements | Serverlessframework](https://www.serverless.com/plugins/serverless-python-requirements)


`serverless-python-requirements` はrequirements.txt で指定したライブラリをLambdaにバンドルすることができます。

```bash
# インストール
sls plugin install -n serverless-python-requirements
```

`serverless.yml` の `plugins` にインストールしたプラグインを設定し、pythonライブラリのビルドをコンテナで行うオプション ( `dockerizePip: true` )と、ライブラリをレイヤーとしてデプロイする設定 ( `layer: true` ) を設定します。

```yml
# --- sample-app/serverless.yml ---

# ... 略 ...
custom:
  pythonRequirements:  # requirements.txt に記載したpythonライブラリをビルドする設定
    dockerizePip: true  # pythonライブラリのビルドをdockerで行う設定
    layer: true  # pythonライブラリをレイヤーとしてデプロイする設定
plugins:
  - serverless-python-requirements
```

# serverless.yml の設定

`package` にはlambdaパッケージに含めるファイルをパターンで定義します。

- [Package | ServerlessFramework](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#package)

```yml
# --- sample-app/serverless.yml ---
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


```yml
# --- sample-app/serverless.yml ---

resources:
  Resources:
    ApiServerRole: # ManagedPolicyArnsとPoliciesを両方利用した例
      Type: AWS::IAM::Role
      Properties:
        RoleName: SampleApp-ApiServerRole
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


```yml
# --- sample-app/serverless.yml ---

functions:
  api:
    handler: main.handler  # main.pyのhandlerをハンドラとして利用する
    timeout: 29
    role: ApiServerRole  # resources配下に実装したロール名
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



```yml
# --- sample-app/serverless.yml ---

provider:
  name: aws
  runtime: python3.9
  stage: ${opt:stage, "dev"}  # ステージ名 (--stageオプションがなければdev)
  region: "ap-northeast-1"  # デプロイするリージョン
  deploymentBucket:
    name: "sls-deploy-gcappr58"  # デプロイアーティファクトを保存するs3バケット
  apiGateway:  # API Gateway v1 REST APIの設定
    # バイナリファイルを返却できるようにする設定
    binaryMediaTypes:
      - '*/*'
```




# アプリ実装

## requirements.txtの作成

```bash
cat <<EOF > requirements.txt
fastapi~=0.99.1
python-jose[cryptography]~=3.3.0
passlib[bcrypt]~=1.7.4
alembic~=1.11.1
PyMySQL~=1.1.0
SQLAlchemy~=2.0.17
mangum~=0.17.0
boto3~=1.27.0
EOF
```

## アプリの実装

```bash
rm handler.py
touch main.py  # serverless.ymlのfunctions.api.handlerに指定したファイル

# lambda関数にインクルードされるファイルを作成
mkdir src static
touch src/env.py static/index.html
```

```py
# --- sample-app/main.py ---

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

```py
# --- sample-app/src/env.py ---

from functools import lru_cache
from pydantic import BaseSettings

class Environment(BaseSettings):
    api_gateway_base_path: str = "/dev"

@lru_cache
def get_env() -> Environment:
    return Environment()
```

```html
<!-- *** sample-app/static/index.html *** -->

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

# デプロイ

```bash
# デプロイ
sls deploy --stage prd

# 削除
sls remove --stage prd
```
