import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

TEST_ACTIVITY = "Programming Class"
TEST_EMAIL = "testuser@example.com"


@pytest.fixture(autouse=True)
def restore_activities():
    """Reset the in-memory activities store before each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert TEST_ACTIVITY in data
    assert isinstance(data[TEST_ACTIVITY]["participants"], list)


def test_signup_for_activity_adds_participant(client):
    # Arrange
    assert TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]

    # Act
    response = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {TEST_EMAIL} for {TEST_ACTIVITY}"
    assert TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]


def test_signup_duplicate_email_returns_400(client):
    # Arrange
    activities[TEST_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity(client):
    # Arrange
    if TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]:
        activities[TEST_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={TEST_EMAIL}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {TEST_EMAIL} from {TEST_ACTIVITY}"
    assert TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]


def test_remove_missing_participant_returns_404(client):
    # Arrange
    assert TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]

    # Act
    response = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={TEST_EMAIL}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
