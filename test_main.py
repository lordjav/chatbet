from .main import app
from .dependencies import calculate_odds
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_stakes():
    response = client.get("/?tournament_id=4584&match_id=25275355")
    stakes = response.json()["result"]

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert 'homeTeam' in stakes
    assert 'awayTeam' in stakes
    assert 'tie' in stakes
    for stake in stakes:
        assert 'name' in stakes[stake]
        assert 'profit' in stakes[stake]
        assert 'odds' in stakes[stake]
        assert 'betId' in stakes[stake]


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

    assert process_time < 3000


def test_calculate_odds():
    profits_to_odds = {1.01:-10000, 1.55:-182, 2.1:110, 6.1:510, 10:900, 23:2200}

    for key, value in profits_to_odds.items():
        assert value == calculate_odds(key)