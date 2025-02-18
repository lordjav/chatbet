from fastapi import HTTPException
from ..dependencies import get_data, calculate_odds
from ..models import Stake, ResultStakes


async def get_market1_data(tournament_id: int, match_id: int) -> ResultStakes:

    # Get data from sportbook API
    data = await get_data(tournament_id, 2)

    # Get match by ID
    match_found = False
    for match in data['result']:
        if match.get("ID") == match_id:
            stakes = match.get("STKS")
            match_found = True
            break

    if match_found == False:
        raise HTTPException(status_code=404, detail="Error: match not found")

    # Save stakes in models
    stake_dict = {}
    for element in stakes:
        new_stake = Stake(
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
    result = ResultStakes(
        homeTeam=stake_dict.get('homeTeam'),
        awayTeam=stake_dict.get('awayTeam'),
        tie=stake_dict.get('tie')
    )
    return result
    
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=f"Error with server: {e}")