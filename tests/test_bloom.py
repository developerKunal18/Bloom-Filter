import pytest
import app as app_module


@pytest.fixture()
def client():
    app_module.bloom = app_module.BloomFilter(size=256, hash_count=4)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


def test_added_value_might_exist(client):
    assert client.post("/api/items", json={"value": "user-100"}).status_code == 201
    assert client.get("/api/check/user-100").get_json()["might_contain"] is True


def test_unknown_value_is_absent_when_bits_are_clear(client):
    client.post("/api/items", json={"value": "known-value"})
    assert client.get("/api/check/definitely-unknown").get_json()["might_contain"] is False


def test_batch_add(client):
    response = client.post("/api/items/batch", json={"values": ["a", "b", "c"]})
    assert response.status_code == 201
    assert response.get_json()["added"] == 3
    assert client.get("/api/check/b").get_json()["might_contain"] is True


def test_invalid_add(client):
    assert client.post("/api/items", json={}).status_code == 400


def test_stats(client):
    client.post("/api/items", json={"value": "a"})
    client.post("/api/items", json={"value": "b"})
    data = client.get("/api/stats").get_json()
    assert data["items_added"] == 2
    assert 0 < data["fill_ratio"] <= 1


def test_empty_filter():
    bloom = app_module.BloomFilter(size=128, hash_count=3)
    assert bloom.might_contain("missing") is False
