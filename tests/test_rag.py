from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_retrieve_endpoint() -> None:
    payload = {
        "query": "What is an open circuit defect in PCB inspection?"
    }
    response = client.post("/api/v1/rag/retrieve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert len(data["retrieved_chunks"]) >= 1


def test_query_endpoint() -> None:
    payload = {
        "query": "What is an open circuit defect in PCB inspection?",
        "include_sources": True,
        "include_chunks": True
    }
    response = client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
