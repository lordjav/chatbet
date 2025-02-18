from .main import app
from .dependencies import calculate_odds
from .authentication import create_access_token
from fastapi.testclient import TestClient
from datetime import timedelta
client = TestClient(app)

# Save JWT in a global variable for using in all tests
JWT: str | None = None

# Test authentication using JWT
def test_access_token():
    global JWT
    JWT = create_access_token(data={"sub": "root"}, expires_delta=timedelta(minutes=1))
    
    response = client.get("/?tournament_id=4584&match_id=25275355", headers={"Authorization": f"Bearer {JWT}"})

    assert response.status_code == 200


# Test authentication with a wrong token
def test_wrong_token():
    fake_jwt = create_access_token(data={"sub": "admin"}, expires_delta=timedelta(minutes=1))

    response = client.get("/?tournament_id=4584&match_id=25275355", headers={"Authorization": f"Bearer {fake_jwt}"})

    assert response.status_code == 401
    assert 'Could not validate credentials' in response.json()['detail']


# Test main endpoint and data structure
def test_get_stakes():
    response = client.get("/?tournament_id=4584&match_id=25275355", headers={"Authorization": f"Bearer {JWT}"})
    response_json = response.json()
    result = response_json["result"]
    over_under = response_json["over_under"]
    handicap = response_json["handicap"]

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert 'homeTeam' in result
    assert 'awayTeam' in result
    assert 'tie' in result
    for stake in result:
        assert 'name' in result[stake]
        assert 'profit' in result[stake]
        assert 'odds' in result[stake]
        assert 'betId' in result[stake]
    assert 'over' in over_under
    assert 'under' in over_under
    assert 'homeTeam' in handicap
    assert 'awayTeam' in handicap


# Test main endpoint with wrong tournament id
def test_wrong_tournament_id():
    response = client.get("/?tournament_id=0000&match_id=25275355", headers={"Authorization": f"Bearer {JWT}"})

    assert response.status_code == 404
    assert response.json() == {"detail":"Error: tournament not found"}


# Test main endpoint with wrong match id
def test_wrong_match_id():
    response = client.get("/?tournament_id=4584&match_id=00000000", headers={"Authorization": f"Bearer {JWT}"})

    assert response.status_code == 404
    assert response.json() == {"detail":"Error: match not found"}


# Test response time is not greater than 7 segs
def test_response_time():
    response = client.get("/?tournament_id=4584&match_id=25275355", headers={"Authorization": f"Bearer {JWT}"})
    str_time = response.headers["X-Process-Time"]
    process_time = int(str_time[:str_time.find(' ')])

    assert process_time < 7000


# Test calculate_odds function
def test_calculate_odds():
    profits_to_odds = {1.01:-10000, 1.55:-182, 2.1:110, 6.1:510, 10:900, 23:2200}

    for key, value in profits_to_odds.items():
        assert value == calculate_odds(key)