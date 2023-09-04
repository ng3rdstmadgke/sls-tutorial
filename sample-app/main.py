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
    return {"hello": env.api_gateway_base_path}

@app.get("/api/world")
def world():
    env = get_env()
    return {"world": env.api_gateway_base_path}

from fastapi import FastAPI, Request, Response
import json

# Starlette - Request: https://www.starlette.io/requests/
# Starlette - Response: https://www.starlette.io/responses/
@app.get("/api/get_test")
async def get_test(request: Request, ):
    print(request.headers)
    print(request.url)
    print(request.method)
    print(request.query_params)
    print(request.client)
    print(await request.body())
    response = {"url": str(request.url)}
    return Response(
        content=json.dumps(response),
        status_code=200,
        headers={"hoge": "fuga"},
        media_type="application/json",
    )

from pydantic import BaseModel

class PostSchema(BaseModel):
    name: str
    age: int

@app.post("/api/post_test")
async def post_test(
    data: PostSchema,
    request: Request
):
    print(request.headers)
    print(request.url)
    print(request.method)
    print(request.query_params)
    print(request.client)
    print(await request.json())
    response = {"url": str(request.url)}
    return Response(
        content=json.dumps(response),
        status_code=200,
        headers={"hoge": "fuga"},
        media_type="application/json",
    )

import boto3
@app.get("/api/list_bucket")
def list_bucket(request: Request):
    client = boto3.client('s3')
    response = client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    print(response)
    return Response(
        content=json.dumps(buckets),
        status_code=200,
        headers=None,
        media_type="application/json",
    )


app.mount("/", StaticFiles(directory=f"./static", html=True), name="static")

handler = Mangum(app)