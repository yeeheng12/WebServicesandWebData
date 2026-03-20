def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "House Sales and Energy Efficiency API is running"
    assert data["version"] == "3.0.0"
    assert data["docs_url"] == "/docs"
    assert data["resources"]["properties"] == "/properties"
    assert data["resources"]["locations"] == "/locations"
    assert data["resources"]["analytics"] == "/analytics"
    assert data["resources"]["energy_certificates"] == "/energy-certificates"
    assert data["security"]["scheme"] == "Bearer JWT"
    assert data["security"]["login"] == "/auth/login"

def test_docs_endpoint_available(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "/auth/login" in data["paths"]
    assert "/properties/" in data["paths"]
    assert "/energy-certificates/" in data["paths"]