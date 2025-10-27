import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestBasicEndpoints:
    """Test basic API endpoints"""

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]

    def test_get_activities(self, client, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        
        # Check specific activity structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestActivitySignup:
    """Test activity signup functionality"""

    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup(self, client, reset_activities):
        """Test duplicate signup prevention"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response1.status_code == 400
        assert "already signed up" in response1.json()["detail"]

    def test_signup_with_encoded_activity_name(self, client, reset_activities):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newcoder@mergington.edu"
        )
        assert response.status_code == 200
        assert "newcoder@mergington.edu" in response.json()["message"]

    def test_signup_with_encoded_email(self, client, reset_activities):
        """Test signup with URL-encoded email"""
        response = client.post(
            "/activities/Chess Club/signup?email=test%2Buser@mergington.edu"
        )
        assert response.status_code == 200


class TestActivityUnregister:
    """Test activity unregister functionality"""

    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregistration when not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_with_encoded_activity_name(self, client, reset_activities):
        """Test unregistration with URL-encoded activity name"""
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_with_encoded_email(self, client, reset_activities):
        """Test unregistration with URL-encoded email"""
        # First add a participant with encoded email
        client.post("/activities/Chess Club/signup?email=test%2Buser@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Chess Club/unregister?email=test%2Buser@mergington.edu"
        )
        assert response.status_code == 200


class TestCompleteWorkflow:
    """Test complete signup and unregister workflows"""

    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup then unregister"""
        email = "workflow@mergington.edu"
        activity = "Math Olympiad"
        
        # Initial state check
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity]["participants"]
        assert email not in initial_participants
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup_response = client.get("/activities")
        after_signup_participants = after_signup_response.json()[activity]["participants"]
        assert email in after_signup_participants
        assert len(after_signup_participants) == len(initial_participants) + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity]["participants"]
        assert email not in final_participants
        assert len(final_participants) == len(initial_participants)

    def test_multiple_participants_management(self, client, reset_activities):
        """Test managing multiple participants for same activity"""
        activity = "Science Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are signed up
        after_signup_response = client.get("/activities")
        participants = after_signup_response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
        assert len(participants) == initial_count + len(emails)
        
        # Unregister one student
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={emails[1]}")
        assert unregister_response.status_code == 200
        
        # Verify partial unregistration
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity]["participants"]
        assert emails[0] in final_participants
        assert emails[1] not in final_participants
        assert emails[2] in final_participants
        assert len(final_participants) == initial_count + len(emails) - 1


class TestDataValidation:
    """Test data validation and edge cases"""

    def test_all_activities_have_required_fields(self, client, reset_activities):
        """Test that all activities have required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities_data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
            
            # Type validation
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Ensure participants are within limits
            assert len(activity_data["participants"]) <= activity_data["max_participants"]

    def test_activity_names_consistency(self, client, reset_activities):
        """Test that activity names are consistent"""
        response = client.get("/activities")
        activities_data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team", 
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity_name in expected_activities:
            assert activity_name in activities_data, f"Missing expected activity: {activity_name}"