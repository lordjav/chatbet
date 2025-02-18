from fastapi import HTTPException
import httpx

BASE_URL = "https://vjq8qplo2h.execute-api.us-east-1.amazonaws.com/test/getMatches"

async def get_data(tournament_id: int, market: int):
    async with httpx.AsyncClient() as external_api:

        # Get data from sportbook API
        raw_data = await external_api.get(f"{BASE_URL}",
                                            params={
                                                "lIds": "13",
                                                "tIds": str(tournament_id),
                                                "cc": "DEF",
                                                "sttIds": str(market)
                                                }
                                            )
        data = raw_data.json()
        if not data["result"]:
            raise HTTPException(status_code=404, detail=f"Error: tournament not found")
        if not data["isSuccess"] or data["hasErrorData"]:
            raise HTTPException(status_code=500, detail="Error with external API: error in data")
        
        return data


# Function: calculate odds base on profit
def calculate_odds(profit):
    if profit < 2.0:
        return round(-100/(profit - 1))
    else:
        return round((profit - 1) * 100)