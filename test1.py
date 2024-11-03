import requests

def test_get_todo_by_id():
    """Test getting a specific TODO item by ID."""
    base_url = "http://localhost:8000"  # Replace with your API base URL
    todo_id = 1  # Replace with the actual ID of a TODO item

    requests.get(f"{base_url}/todos/{todo_id}")

    # assert response.status_code == 200
    # todo_data = response.json()
    # assert "id" in todo_data
    # assert "title" in todo_data
    # assert "description" in todo_data
    # assert "completed" in todo_data
while True:
    test_get_todo_by_id()