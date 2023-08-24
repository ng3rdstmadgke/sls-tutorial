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

app.mount("/", StaticFiles(directory=f"./static", html=True), name="static")

handler = Mangum(app)