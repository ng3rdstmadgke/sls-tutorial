# 参考

- [Tutorial | Serverless Framework](https://www.serverless.com/framework/docs/tutorial)
- [FastAPI](https://fastapi.tiangolo.com/)

# ホストの環境準備

## Python3.11のインストール

Amazon Linux 2023

```bash
$ sudo dnf update -y
$ sudo dnf install python3.11
```

Ubuntu

```bash
$ sudo apt update
$ sudo apt install python3.11
```


## Dockerインストール

Amazon Linux 2023

```bash

# dockerのインストール
$ sudo dnf update -y
$ sudo dnf install -y docker
```

そのほかのOS

https://docs.docker.com/engine/install/

## Dockerの初期設定

```bash
# サービスの有効化・起動
$ sudo systemctl enable docker
$ sudo systemctl start docker

# ユーザーをdockerグループに追加
$ sudo usermod -aG docker $USER

# 再ログインしてdockerコマンドを実行できるか確認
$ exit
$ docker ps
```

# サンプルソースコードを動かしてみる

```bash
$ bin/run.sh sample
# localhost:8080をポートフォワードして以下のURLにアクセス
# - http://localhost:8080/
# - http://localhost:8080/api/docs
```


# AWSリソース作成

## s3バケット作成

ServerlessFrameworkのdeployで利用するs3バケットを作成してください。

# サーバーレスフレームワークのインストール

## nvmインストール

https://github.com/nvm-sh/nvm

```bash
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

$ source ~/.bashrc

# インストール可能なnodeのバージョン一覧
$ nvm ls-remote

# LTS(v20.*)をインストール
$ nvm install lts/iron

# インストールしたバージョンをアクティベート
$ nvm use lts/iron

# バージョン確認
$ node --version
v20.11.1
```

## serverless framework インストール

```bash
# インストール
$ npm install -g serverless

# slsコマンドが利用できるか確認
$ sls -v
Framework Core: 3.38.0
Plugin: 7.2.3
SDK: 4.5.1
```


# プロジェクト作成

```bash
# 任意のプロジェクト名
$ PROJECT_NAME=sample

# プロジェクト作成
$ mkdir -p $PROJECT_NAME

# プロジェクトにcd
$ cd $PROJECT_NAME
```

ファイル・ディレクトリの作成

```bash
# .gitignore作成
$ cat <<EOF > .gitignore
# Distribution / packaging
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Serverless directories
.serverless
EOF

# requirements.txt
$ cat <<EOF > requirements.txt
fastapi[all]~=0.110.0
PyMySQL~=1.1.0
SQLAlchemy~=2.0.27
mangum~=0.17.0
boto3~=1.34.54
EOF

# serverless frameworkの設定ファイル
cat <<EOF > serverless.yml
service: sls-tutorial-${PROJECT_NAME}

frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.11
EOF

# ディレクトリ作成
mkdir -p src/routers src/templates src/utils static

# lambda関数のエントリーポイントとなるファイル
touch main.py

# 環境変数定義ファイル
touch src/env.py

# view・api定義ファイル
touch src/routers/views.py src/routers/apis.py

# テンプレートファイル
touch src/templates/base.html src/templates/index.html src/templates/edit_distance.html

# 編集距離関数定義ファイル
touch src/utils/edit_distance.py

touch static/.gitkeep
```

ディレクトリ構成

```
- $PROJECT_NAME
  - main.py  # lambda関数のハンドラとして指定するファイル
  - src/  # main.pyから参照するPythonファイル
    - routers/
      - views.py  # htmlを返却するルートを定義するファイル
      - apis.py  # APIを定義するファイル
    - templates/
      - base.html  # テンプレートの共通部分を定義するファイル
      - index.html  # topページのテンプレート
      - edit_distance.html  # Edit Distanceページのテンプレート
    - utils/
      - edit_distance.py  # EditDistanceの関数定義ファイル
    - env.py  # 環境変数定義ファイル
  - static/  # 静的ファイル置き場
  - requirements.txt
  - serverless.yml  # serverless frameworkの設定ファイル
  - .gitignore
```

# アプリ実装

## requirements.txtの作成

```bash
# venv
$ python3.11 -m venv .venv
$ source .venv/bin/activate

# requirements.txt のインストール
$ pip install -r requirements.txt
```

## アプリの実装

`main.py`

```py
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from src.routers import apis, views
from src.env import get_env

app = FastAPI(
    redoc_url="/api/redoc",
    docs_url="/api/docs",
    openapi_url="/api/docs/openapi.json",
    root_path=get_env().api_gateway_base_path,
)
allow_origins = ["*"]

app.include_router(views.router)
app.include_router(apis.router, prefix="/api")

# 静的ファイルの配信
app.mount("/", StaticFiles(directory=f"./static", html=True), name="static")

# Lambdaのハンドラ
from mangum import Mangum
handler = Mangum(app)

```

`src/env.py`

```py
from functools import lru_cache
from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    api_gateway_base_path: str = ""

@lru_cache
def get_env() -> Environment:
    return Environment()
```

### APIの実装

edit distanceの関数を定義

`src/utils/edit_distance.py`

```python
"""
src を dst に変換するための編集距離を計算するメソッド
src       : 編集対象文字列
dst       : 目標文字列
add     : src に一文字追加するコスト
remove  : src から一文字削除するコスト
replace : src を一文字置換するコスト
"""
def edit_dist(src, dst, add=1, remove=1, replace=1):
  len_a = len(src) + 1
  len_b = len(dst) + 1
  # 配列の初期化
  arr = [[-1 for col in range(len_a)] for row in range(len_b)]
  arr[0][0] = 0
  for row in range(1, len_b):
    arr[row][0] = arr[row - 1][0] + add
  for col in range(1, len_a):
    arr[0][col] = arr[0][col - 1] + remove
  # 編集距離の計算
  def go(row, col):
    if (arr[row][col] != -1):
      return arr[row][col]
    else:
      dist1 = go(row - 1, col) + add
      dist2 = go(row, col - 1) + remove
      dist3 = go(row - 1, col - 1)
      arr[row][col] = min(dist1, dist2, dist3) if (dst[row - 1] == src[col - 1]) else min(dist1, dist2, dist3 + replace)
      return arr[row][col]
  return go(len_b - 1, len_a - 1)

```

`src/routers/apis.py`

```python
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from src.utils import edit_dist

router = APIRouter()
class EditDistancePostSchema(BaseModel):
    src: str
    dst: str

@router.post("/edit_distance")
def edit_distance(
    data: EditDistancePostSchema,
):
    dist = edit_dist(data.src, data.dst)
    return {
        "src": data.src,
        "dst": data.dst,
        "edit_distance": dist,
    }
```

### ビューの実装

`src/routers/views.py`

```python
from fastapi import Request
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.env import get_env

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "base_path": get_env().api_gateway_base_path
        }
    )

@router.get("/edit_distance")
async def edit_distance(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="edit_distance.html",
        context={
            "base_path": get_env().api_gateway_base_path
        }
    )

```

### テンプレートの実装


`src/templates/base.html`

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
  {% block head %}
  {% endblock %}
  <title>
    {% block title %}{% endblock %}
  </title>
</head>
<body>
  <div>
    <!-- Header -->
    <nav class="navbar navbar-expand-md bg-dark border-bottom border-bottom-dark" data-bs-theme="dark">
      <div class="container-fluid">
        <a class="navbar-brand" href="{{ base_path }}/">MyApps</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavDropdown">
          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link active" aria-current="page" href="{{ base_path }}/">Top</a>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Apps
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="{{ base_path }}/edit_distance">Edit Distance</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="container mt-3">
      {% block content %}{% endblock %}
    </div>
  </div>
</body>
</html>
```

`src/templates/index.html`

```html
{% extends "base.html" %}
{% block title %}Top{% endblock %}
{% block content %}
  <h1>Apps</h1>
  <ol>
    <li><a href="{{ base_path }}/edit_distance">Edit Distance</a></li>
  </ol>
{% endblock %}
```

`src/templates/edit_distance.html`

```html
{% extends "base.html" %}
{% block title %}Top{% endblock %}
{% block content %}
    <h1>Edit Distance</h1>
    <form id="js_form">
      <div class="row mb-3">
        <label for="js_src" class="col-sm-2 col-form-label">src text</label>
        <div class="col-sm-10">
          <input type="text" class="form-control" id="js_src">
        </div>
      </div>
      <div class="row mb-3">
        <label for="js_dst" class="col-sm-2 col-form-label">dst text</label>
        <div class="col-sm-10">
          <input type="text" class="form-control" id="js_dst">
        </div>
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    <div id='js_response' class="mt-5 fs-2">
    </div>
    <script>
      document.getElementById("js_form").addEventListener("submit", async function(e) {
        e.preventDefault()
        var base_path = "{{ base_path }}"
        var url = `${base_path}/api/edit_distance`
        var src = document.getElementById("js_src").value
        var dst = document.getElementById("js_dst").value
        var response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({src: src, dst: dst})
        })
        var data = await response.json()
        document.getElementById('js_response').textContent = "Edit distance: " + data.edit_distance
      })
    </script>
{% endblock %}
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
    dockerizePip: true  # layerの作成をdockerで行う
    layer: true  # pythonライブラリをレイヤーとしてデプロイする設定

plugins:
  - serverless-python-requirements
```

## serverless.yml の設定


`package` にはlambdaパッケージに含めるファイルをパターンで定義します。

- [Package | ServerlessFramework](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml#package)

`${PROJECT_NAME}/serverless.yml`

```yml
# ... 略 ...

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
# ... 略 ...

resources:
  Resources:
    # Lambdaのタスクロール
    AppRole:
      Type: AWS::IAM::Role
      Properties:
        RoleName: ${self:service}-${self:provider.stage}-AppRole
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
    AppRolePolicy:
      Type: AWS::IAM::ManagedPolicy
      Properties:
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
        ManagedPolicyName: ${self:service}-${self:provider.stage}-AppRolePolicy
        Roles:
          - Ref: AppRole
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
# ... 略 ...

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
# ... 略 ...

provider:
  name: aws
  runtime: python3.11
  stage: ${opt:stage, "dev"}  # ステージ名 (--stageオプションがなければdev)
  region: "ap-northeast-1"  # デプロイするリージョン
  deploymentBucket:
    name: "sls-deploy-gcappr58"  # デプロイアーティファクトを保存するs3バケット
  apiGateway:  # API Gateway v1 REST APIの設定
    # バイナリファイルを返却できるようにする設定
    binaryMediaTypes:
      - '*/*'

# ... 略 ...
```


# デプロイ

```bash
# プラグインなどパッケージのインストール (一応)
npm install

# デプロイ
sls deploy --stage prd

# デプロイしたAPIにアクセス
# - https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/
# - https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/api/docs

# 削除
sls remove --stage prd
```
