from pydantic import BaseModel


class Stake(BaseModel):
    name: str
    profit: float
    odds: int
    betId: int


class BaseMarket(BaseModel):
    homeTeam: Stake
    awayTeam: Stake


class ResultStakes(BaseMarket):
    tie: Stake


class OverUnderStakes(BaseModel):
    over: Stake
    under: Stake


class HandicapStakes(BaseMarket):
    pass


class get_odds(BaseModel):
    status: str
    result: ResultStakes | None
    over_under: OverUnderStakes | None
    handicap: HandicapStakes | None
