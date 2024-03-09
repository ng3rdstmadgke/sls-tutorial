from functools import lru_cache
from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    api_gateway_base_path: str = ""

@lru_cache
def get_env() -> Environment:
    return Environment()
