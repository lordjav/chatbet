from fastapi import FastAPI, Request
from .models import get_odds
from .markets.market1 import get_market1_data
import time

app = FastAPI()


# Middelware: mesure response time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.0f} ms"
    return response


# Main endpoint
@app.get("/", response_model=get_odds)
async def get_stakes(tournament_id: int, match_id: int):

    market1_stakes = await get_market1_data(tournament_id, match_id)
    # market2_stakes = await get_market2_data(tournament_id, match_id)
    # market3_stakes = await get_market3_data(tournament_id, match_id)

    response: get_odds = get_odds(
        status="success", 
        result=market1_stakes,
        handicap=None,
        over_under=None
        )
    
    return response

    
        