from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

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
