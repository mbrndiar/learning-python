"""
Chapter 17, Lesson 1: A Minimal Flask App and Test Client

Purpose: create one Flask application, register direct routes, observe the
request proxy, and test requests without starting a server.

Prerequisite: Chapter 16's HTTP method/path/status/body model and Chapter 10
decorators.

Run from the repository root:

    python lessons/17_web_apis_with_flask_and_fastapi/01_flask_minimal_app_and_test_client.py
"""

from flask import Flask, request

# Step 1: one Flask instance is the WSGI application. __name__ identifies this
# module so Flask can locate resources such as templates and static files.
app = Flask(__name__)


# Step 2: the decorator registers this function for GET /health.
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Step 3: request is a context-local proxy. Flask resolves it only while it is
# dispatching a request. `json=...` in the test client sets JSON content type.
@app.post("/echo")
def echo() -> tuple[dict[str, object], int]:
    payload: object = request.get_json()
    if not isinstance(payload, dict):
        return {"error": {"code": "invalid_request"}}, 400
    return {"received": payload}, 201


if __name__ == "__main__":
    # Step 4: the test client runs the complete Flask dispatch in process.
    with app.test_client() as client:
        health_response = client.get("/health")
        created_response = client.post("/echo", json={"title": "Learn Flask"})
        wrong_method = client.get("/echo")

    assert health_response.status_code == 200
    assert health_response.get_json() == {"status": "ok"}
    assert created_response.status_code == 201
    assert created_response.get_json() == {"received": {"title": "Learn Flask"}}
    assert wrong_method.status_code == 405

    print("health:", health_response.status_code, health_response.get_json())
    print("echo:", created_response.status_code, created_response.get_json())
    print("wrong method:", wrong_method.status_code)
