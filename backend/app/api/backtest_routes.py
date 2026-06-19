from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_backtest():
    return {"message": "Backtest endpoint ready", "result": {}}
