from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_schools_lists_default_school():
    response = client.get("/schools")
    assert response.status_code == 200
    data = response.json()
    assert "Mergington High School" in data
    assert data["Mergington High School"]["short_name"] == "MHS"
    assert data["Mergington High School"]["join_code"] == "MHS123"


def test_create_school_and_join_with_code():
    response = client.post(
        "/schools",
        json={"name": "North Valley Academy", "short_name": "NVA", "join_code": "NOVA42"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "North Valley Academy"
    assert payload["short_name"] == "NVA"

    join_response = client.post(
        "/schools/North Valley Academy/join",
        params={"email": "student@northvalley.edu", "join_code": "NOVA42"},
    )
    assert join_response.status_code == 200
    assert "student@northvalley.edu" in join_response.json()["members"]


def test_activities_can_be_filtered_by_school():
    response = client.get("/activities", params={"school": "Mergington High School"})
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "School" in data["Chess Club"] or "school" in data["Chess Club"]
