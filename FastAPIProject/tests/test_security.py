def test_viewer_cannot_create_property(client, viewer_headers, property_payload):
    response = client.post("/properties/", json=property_payload, headers=viewer_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions: editor or admin role required"


def test_editor_can_create_property(client, editor_headers, property_payload):
    response = client.post("/properties/", json=property_payload, headers=editor_headers)
    assert response.status_code == 201
    assert response.json()["price"] == 275000.0


def test_admin_can_create_property(client, admin_headers, property_payload):
    payload = dict(property_payload)
    payload["transaction_id"] = "txn-admin-create-001"

    response = client.post("/properties/", json=payload, headers=admin_headers)
    assert response.status_code == 201


def test_viewer_cannot_update_property(client, viewer_headers, sample_property):
    response = client.patch(
        f"/properties/{sample_property.id}",
        json={"price": 260000.0},
        headers=viewer_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions: editor or admin role required"


def test_editor_can_update_property(client, editor_headers, sample_property):
    response = client.patch(
        f"/properties/{sample_property.id}",
        json={"price": 260000.0},
        headers=editor_headers,
    )
    assert response.status_code == 200
    assert response.json()["price"] == 260000.0


def test_editor_cannot_delete_property(client, editor_headers, sample_property):
    response = client.delete(f"/properties/{sample_property.id}", headers=editor_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions: admin role required"


def test_admin_can_delete_property(client, admin_headers, sample_property):
    response = client.delete(f"/properties/{sample_property.id}", headers=admin_headers)
    assert response.status_code == 204


def test_missing_token_on_protected_route_returns_401(client, property_payload):
    response = client.post("/properties/", json=property_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_invalid_token_on_protected_route_returns_401(client, property_payload):
    response = client.post(
        "/properties/",
        json=property_payload,
        headers={"Authorization": "Bearer bad-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"