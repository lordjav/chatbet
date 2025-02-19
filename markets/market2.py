from dependencies import get_data, get_favorite_stake
from models import HandicapStakes


async def get_market2_data(tournament_id: int, match_id: int) -> HandicapStakes:

    # Get data from sportbook API
    data = await get_data(tournament_id, 2)

    # Get favorite stakes and return them
    stakes = get_favorite_stake(data, match_id)
    
    handicap = HandicapStakes(
        homeTeam=stakes[0],
        awayTeam=stakes[1],
    )

    return handicap
