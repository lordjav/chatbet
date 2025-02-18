from datetime import timedelta
from mangum import Mangum
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from .models import get_odds, Token, User
from .markets.market1 import get_market1_data
from .markets.market2 import get_market2_data
from .markets.market3 import get_market3_data
from .authentication import *
import time


app = FastAPI()
handler = Mangum(app)


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
async def get_stakes(tournament_id: int, match_id: int, current_user: Annotated[User, Depends(get_current_user)]):

    market1_stakes = await get_market1_data(tournament_id, match_id)
    market2_stakes = await get_market2_data(tournament_id, match_id)
    market3_stakes = await get_market3_data(tournament_id, match_id)

    response: get_odds = get_odds(
        status="success", 
        result=market1_stakes,
        handicap=market2_stakes,
        over_under=market3_stakes
        )
    
    return response


# Authentication endpoint
@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")