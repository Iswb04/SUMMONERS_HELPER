from fastapi import FastAPI
try:
    from API_counter import router as counters_router
    from API_advantage import router as advantages_router
except ImportError:
    from .API_counter import router as counters_router
    from .API_advantage import router as advantages_router

app = FastAPI()

app.include_router(counters_router)
app.include_router(advantages_router)


# Comando para rodar (na raiz do projeto):
# uvicorn league_code.API_main:app --reload

# http://127.0.0.1:8000/counters
# http://127.0.0.1:8000/advantages


