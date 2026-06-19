from fastapi import APIRouter
from app.api.data_routes import router as data_router
from app.api.strategy_routes import router as strategy_router
from app.api.backtest_routes import router as backtest_router
from app.api.order_routes import router as order_router
from app.api.dashboard_routes import router as dashboard_router

api_router = APIRouter(prefix="/api")
api_router.include_router(data_router, prefix="/data", tags=["data"])
api_router.include_router(strategy_router, prefix="/strategies", tags=["strategies"])
api_router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
api_router.include_router(order_router, prefix="/orders", tags=["orders"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
