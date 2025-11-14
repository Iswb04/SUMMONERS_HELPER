from fastapi import FastAPI
from SQL_LEAGUE.API_counter import router as counters_router
from SQL_LEAGUE.API_advantage import router as advantages_router

app = FastAPI()

app.include_router(counters_router)
app.include_router(advantages_router)


# uvicorn SQL_LEAGUE.API_main:app --reload

# http://127.0.0.1:8000/counters
# http://127.0.0.1:8000/advantages

