from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import httpx
import time

app = FastAPI()

class stake(BaseModel):
    name: str
    profit: float
    odds: int
    betId: int


class stakes_by_match(BaseModel):
    homeTeam: stake
    awayTeam: stake
    tie: stake | None


# Function: calculate odds base on profit
def calculate_odds(profit):
    if profit < 2.0:
        return int(-100/(profit - 1))
    else:
        return int((profit - 1) * 100)


# Middelware: mesure response time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f} segs"
    return response


# Main endpoint
@app.get("/", response_model=stakes_by_match)
async def get_matches(tournament_id: int, match_id: int):
    async with httpx.AsyncClient() as external_api:

        # Try to get data from sportbook API
        try:
            response = await external_api.get(f"https://vjq8qplo2h.execute-api.us-east-1.amazonaws.com/test/getMatches?lIds=13&tIds={tournament_id}&cc=DEF&sttIds=1")

        except httpx._exceptions as e:
            raise HTTPException(status_code=500, detail=f"Error with external API: {e}")

        try:
            # Get match by ID
            matches = response.json()
            for match in matches['result']:
                if match.get("ID") == match_id:
                    stakes = match.get("STKS")
                    break
            
            # Save stakes in models
            stake_dict = {}
            for element in stakes:
                new_stake = stake(
                    name = element.get("NM", {}).get("13"),
                    profit = element["FCR"],
                    betId = element["ID"],
                    odds = calculate_odds(element["FCR"])
                )
                match element.get("CD"):
                    case 1:
                        stake_dict["homeTeam"] = new_stake
                    case 2:
                        stake_dict["tie"] = new_stake
                    case 3:
                        stake_dict["awayTeam"] = new_stake
            
            # Group stakes by match
            result = stakes_by_match(
                homeTeam=stake_dict.get('homeTeam'),
                awayTeam=stake_dict.get('awayTeam'),
                tie=stake_dict.get('tie')
            )
            return result
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with server: {e}")
            