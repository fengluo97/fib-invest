from fastapi import APIRouter
from app.strategy.registry import registry

router = APIRouter()


@router.get("")
async def list_strategies():
    types = registry.list_all()
    return {"strategies": list(types.keys())}
