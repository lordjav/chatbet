from fastapi import HTTPException
import httpx
from models import Stake, FavoriteStake

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


# Function: calculate odds based on profit
def calculate_odds(profit):
    if profit < 2.0:
        return round(-100/(profit - 1))
    else:
        return round((profit - 1) * 100)
    

# Get favorite stakes by find the smallest factor difference beetween every pair of stakes
def get_favorite_stake(data: any, match_id: int):
    # Get match by ID
    match_found = False
    for match in data['result']:
        if match.get("ID") == match_id:
            stakes = match.get("STKS")
            match_found = True
            break

    if match_found == False:
        raise HTTPException(status_code=404, detail="Error: match not found")

    # Sort stakes
    sorted_stakes = sorted(stakes, key=lambda s: (s['CD'], s['ARG']))
    favorite: FavoriteStake = FavoriteStake()
    length = len(sorted_stakes)

    # Find pairs of stakes
    for i in range(int(length/2)):
        if sorted_stakes[i]['SS'] == True:
            stake2_index = length - 1 - i
        else:
            stake2_index = int(length/2 + i)

        # Find the smallest factors difference
        factor_diff: float = abs(sorted_stakes[i]['FCR'] - sorted_stakes[stake2_index]['FCR'])
        if factor_diff < favorite.factor_difference:
            favorite.factor_difference = factor_diff
            favorite.stake1 = sorted_stakes[i]
            favorite.stake2 = sorted_stakes[stake2_index]
    
    # Save stakes as models
    stake1 = Stake(
        name = favorite.stake1.get("NM", {}).get("13") + " " + str(favorite.stake1.get("ARG")),
        profit = favorite.stake1["FCR"],
        betId = favorite.stake1["ID"],
        odds = calculate_odds(favorite.stake1["FCR"])
    )
    stake2 = Stake(
        name = favorite.stake2.get("NM", {}).get("13") + " " + str(favorite.stake2.get("ARG")),
        profit = favorite.stake2["FCR"],
        betId = favorite.stake2["ID"],
        odds = calculate_odds(favorite.stake2["FCR"])
    )

    return [stake1, stake2]