# 参考

- [Tutorial | Serverless Framework](https://www.serverless.com/framework/docs/tutorial)
- [FastAPI](https://fastapi.tiangolo.com/)

# 手順

```bash
mkdir sls-tutorial
cd sls-tutorial

# インストール
npm install serverless

# プロジェクトの初期化
npx serverless
```

```
Creating a new serverless project

? What do you want to make? AWS - Python - HTTP API  ★ 選択
? What do you want to call this project? sls-tutorial  ★ プロジェクト名

✔ Project successfully created in sls-tutorial folder

? Do you want to login/register to Serverless Dashboard? Yes  ★ ログイン
Logging into the Serverless Dashboard via the browser
If your browser does not open automatically, please open this URL:
https://app.serverless.com?client=cli&transactionId=fdHsAGXLTKqOoRZhJKqWr

✔ You are now logged into the Serverless Dashboard


✔ Your project is ready to be deployed to Serverless Dashboard (org: "ktamido", app: "sls-tutorial")

? Do you want to deploy now? Yes  ★ 今すぐデプロイするか

Deploying sls-tutorial to stage dev (us-east-1)

✔ Service deployed to stack sls-tutorial-dev (108s)

dashboard: https://app.serverless.com/ktamido/apps/sls-tutorial/sls-tutorial/dev/us-east-1
endpoint: GET - https://pycosg3j0e.execute-api.us-east-1.amazonaws.com/
functions:
  hello: sls-tutorial-dev-hello (85 kB)

What next?
Run these commands in the project directory:

serverless deploy    Deploy changes
serverless info      View deployed endpoints and resources
serverless invoke    Invoke deployed functions
serverless --help    Discover more commands
```

## Serverless Python Requirements プラグインの導入

- [Serverless Python Requirements](https://www.serverless.com/plugins/serverless-python-requirements)


```bash
npx sls plugin install -n serverless-python-requirements

```