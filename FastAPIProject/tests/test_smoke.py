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