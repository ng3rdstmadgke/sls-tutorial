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