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


class GetOdds(BaseModel):
    status: str
    result: ResultStakes | None
    over_under: OverUnderStakes | None
    handicap: HandicapStakes | None


class FavoriteStake(BaseModel):
    factor_difference: float | None = 100.0
    stake1: dict | None = None
    stake2: dict | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str