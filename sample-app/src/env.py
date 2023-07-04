from functools import lru_cache
from pydantic import BaseSettings

class Environment(BaseSettings):
    api_gateway_base_path: str = "/dev"

@lru_cache
def get_env() -> Environment:
    return Environment()