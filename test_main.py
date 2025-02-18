from .main import app
from .dependencies import calculate_odds
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_stakes():
    response = client.get("/?tournament_id=4584&match_id=25275355")
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


def test_wrong_tournament_id():
    response = client.get("/?tournament_id=0000&match_id=25275355")

    assert response.status_code == 404
    assert response.json() == {"detail":"Error: tournament not found"}


def test_wrong_match_id():
    response = client.get("/?tournament_id=4584&match_id=00000000")

    assert response.status_code == 404
    assert response.json() == {"detail":"Error: match not found"}


def test_response_time():
    response = client.get("/?tournament_id=4584&match_id=25275355")
    str_time = response.headers["X-Process-Time"]
    process_time = int(str_time[:str_time.find(' ')])

    assert process_time < 7000


def test_calculate_odds():
    profits_to_odds = {1.01:-10000, 1.55:-182, 2.1:110, 6.1:510, 10:900, 23:2200}

    for key, value in profits_to_odds.items():
        assert value == calculate_odds(key)