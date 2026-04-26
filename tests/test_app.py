import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_root_redirects():
    """Test that GET / redirects to /static/index.html"""
    # Arrange: No special setup needed

    # Act: Make GET request to root without following redirects
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect with status 307
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all():
    """Test that GET /activities returns all activities"""
    # Arrange: No special setup needed

    # Act: Make GET request to activities
    response = client.get("/activities")

    # Assert: Should return 200 and the activities dict
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_post_signup_success():
    """Test successful signup for an activity"""
    # Arrange: Use an activity and email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # Verify the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]


def test_post_signup_duplicate_fails():
    """Test that signing up twice fails"""
    # Arrange: Use an activity and email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in Chess Club

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 with error message
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]


def test_post_signup_nonexistent_activity_fails():
    """Test signup for nonexistent activity fails"""
    # Arrange: Use a fake activity name
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 with error message
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_delete_signup_success():
    """Test successful unregistration from an activity"""
    # Arrange: Use an activity and email that is signed up
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already in Programming Class

    # Act: Make DELETE request to signup
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" in data["message"]

    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity_name]["participants"]


def test_delete_signup_not_signed_up_fails():
    """Test that unregistering when not signed up fails"""
    # Arrange: Use an activity and email not signed up
    activity_name = "Basketball Team"
    email = "notsignedup@mergington.edu"

    # Act: Make DELETE request to signup
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 with error message
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" in data["detail"]


def test_delete_signup_nonexistent_activity_fails():
    """Test unregistration from nonexistent activity fails"""
    # Arrange: Use a fake activity name
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act: Make DELETE request to signup
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 with error message
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]