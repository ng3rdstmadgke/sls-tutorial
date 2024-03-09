from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from src.utils.edit_distance import edit_dist

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
