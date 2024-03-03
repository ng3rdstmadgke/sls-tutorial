from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from src.routers import edit_distance, views
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

app.include_router(views.router)
app.include_router(edit_distance.router, prefix="/api")

# 静的ファイルの配信
app.mount("/", StaticFiles(directory=f"./static", html=True), name="static")

handler = Mangum(app)