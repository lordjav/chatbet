from ..dependencies import get_data, get_favorite_stake
from ..models import OverUnderStakes


async def get_market3_data(tournament_id: int, match_id: int) -> OverUnderStakes:

    # Get data from sportbook API
    data = await get_data(tournament_id, 3)

    stakes = get_favorite_stake(data, match_id)
        
    over_under = OverUnderStakes(
        over=stakes[0],
        under=stakes[1],
    )
    return over_under
