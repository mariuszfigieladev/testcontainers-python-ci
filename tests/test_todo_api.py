"""
Integration test suite for the Todo REST API using PostgREST and Testcontainers.
"""


def test_healthcheck(api_client):
    """
    Verify that the API root endpoint is reachable and returns HTTP 200 OK.

    Args:
        api_client (requests.Session): Pre-configured HTTP client session.
    """
    response = api_client.get(api_client.base_url)
    assert response.status_code == 200


def test_create_and_get_todo(api_client):
    """
    Verify E2E flow for todo item creation and retrieval.

    Steps:
    1. Send POST request to create a new todo item.
    2. Assert HTTP status code 201 Created and validate response fields.
    3. Send GET request using the generated ID to verify database persistence.

    Args:
        api_client (requests.Session): Pre-configured HTTP client session.
    """
    payload = {"title": "Kupić mleko", "completed": False}
    headers = {"Prefer": "return=representation"}
    
    create_res = api_client.post(
        f"{api_client.base_url}/todos", 
        json=payload, 
        headers=headers
    )
    assert create_res.status_code == 201

    created_todo = create_res.json()[0]
    assert "id" in created_todo
    assert created_todo["title"] == payload["title"]
    assert created_todo["completed"] is False

    get_res = api_client.get(f"{api_client.base_url}/todos?id=eq.{created_todo['id']}")
    assert get_res.status_code == 200
    assert get_res.json()[0]["title"] == payload["title"]


def test_validation_error(api_client):
    """
    Verify API error handling when submitting an invalid payload.

    Asserts that attempting to create a todo item without the mandatory 'title'
    field results in an HTTP 400 Bad Request or HTTP 422 Unprocessable Entity.

    Args:
        api_client (requests.Session): Pre-configured HTTP client session.
    """
    invalid_payload = {"completed": True}
    response = api_client.post(f"{api_client.base_url}/todos", json=invalid_payload)
    assert response.status_code in (400, 422)