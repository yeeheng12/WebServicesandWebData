from app import models

def test_list_energy_certificates_returns_items_and_pagination(
    client, sample_certificate
):
    response = client.get("/energy-certificates/")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["total"] == 1
    assert len(data["items"]) == 1


def test_filter_energy_certificates_by_property_id(
    client, sample_property, sample_certificate
):
    response = client.get(f"/energy-certificates/?property_id={sample_property.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 1
    assert data["items"][0]["property_id"] == sample_property.id


def test_get_energy_certificate_by_id(client, sample_certificate):
    response = client.get(f"/energy-certificates/{sample_certificate.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_certificate.id
    assert data["lmk_key"] == "LMK-001"


def test_get_missing_energy_certificate_returns_404(client):
    response = client.get("/energy-certificates/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Energy certificate not found"


def test_editor_can_create_energy_certificate(
    client, editor_headers, certificate_payload
):
    response = client.post(
        "/energy-certificates/",
        json=certificate_payload,
        headers=editor_headers,
    )
    assert response.status_code == 201

    data = response.json()
    assert data["lmk_key"] == "LMK-CREATE-001"
    assert data["property_id"] == certificate_payload["property_id"]


def test_create_energy_certificate_for_missing_property_returns_404(
    client, editor_headers, certificate_payload
):
    payload = dict(certificate_payload)
    payload["property_id"] = 999999
    payload["lmk_key"] = "LMK-NO-PROPERTY"

    response = client.post(
        "/energy-certificates/",
        json=payload,
        headers=editor_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


def test_create_energy_certificate_duplicate_lmk_key_returns_409(
    client, editor_headers, sample_certificate, certificate_payload
):
    payload = dict(certificate_payload)
    payload["lmk_key"] = sample_certificate.lmk_key

    response = client.post(
        "/energy-certificates/",
        json=payload,
        headers=editor_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "lmk_key already exists"


def test_create_energy_certificate_invalid_rating_returns_422(
    client, editor_headers, certificate_payload
):
    payload = dict(certificate_payload)
    payload["current_energy_rating"] = "Z"

    response = client.post(
        "/energy-certificates/",
        json=payload,
        headers=editor_headers,
    )
    assert response.status_code == 422


def test_create_energy_certificate_invalid_efficiency_returns_422(
    client, editor_headers, certificate_payload
):
    payload = dict(certificate_payload)
    payload["current_energy_efficiency"] = 120

    response = client.post(
        "/energy-certificates/",
        json=payload,
        headers=editor_headers,
    )
    assert response.status_code == 422


def test_editor_can_patch_energy_certificate(
    client, editor_headers, sample_certificate
):
    response = client.patch(
        f"/energy-certificates/{sample_certificate.id}",
        json={"current_energy_rating": "B", "current_energy_efficiency": 78.0},
        headers=editor_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["current_energy_rating"] == "B"
    assert data["current_energy_efficiency"] == 78.0


def test_patch_energy_certificate_missing_certificate_returns_404(
    client, editor_headers
):
    response = client.patch(
        "/energy-certificates/999999",
        json={"current_energy_rating": "B"},
        headers=editor_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Energy certificate not found"


def test_patch_energy_certificate_to_missing_property_returns_404(
    client, editor_headers, sample_certificate
):
    response = client.patch(
        f"/energy-certificates/{sample_certificate.id}",
        json={"property_id": 999999},
        headers=editor_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


def test_patch_energy_certificate_duplicate_lmk_key_returns_409(
    client, editor_headers, db_session, sample_property, editor_user, sample_certificate
):
    second = models.EnergyCertificate(
        property_id=sample_property.id,
        lmk_key="LMK-SECOND",
        current_energy_rating="D",
        potential_energy_rating="C",
        current_energy_efficiency=60.0,
        potential_energy_efficiency=70.0,
        total_floor_area=81.0,
        created_by_user_id=editor_user.id,
        updated_by_user_id=editor_user.id,
    )
    db_session.add(second)
    db_session.commit()
    db_session.refresh(second)

    response = client.patch(
        f"/energy-certificates/{second.id}",
        json={"lmk_key": sample_certificate.lmk_key},
        headers=editor_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "lmk_key already exists"

def test_energy_certificate_create_without_token_returns_401(
    client, certificate_payload
):
    response = client.post("/energy-certificates/", json=certificate_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_energy_certificate_create_with_invalid_token_returns_401(
    client, certificate_payload
):
    response = client.post(
        "/energy-certificates/",
        json=certificate_payload,
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_viewer_cannot_create_energy_certificate(
    client, viewer_headers, certificate_payload
):
    response = client.post(
        "/energy-certificates/",
        json=certificate_payload,
        headers=viewer_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions: editor or admin role required"


def test_viewer_cannot_patch_energy_certificate(
    client, viewer_headers, sample_certificate
):
    response = client.patch(
        f"/energy-certificates/{sample_certificate.id}",
        json={"current_energy_rating": "B"},
        headers=viewer_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions: editor or admin role required"


def test_energy_certificates_invalid_limit_returns_422_or_400(
    client, sample_certificate
):
    response = client.get("/energy-certificates/?limit=0")
    assert response.status_code in (400, 422)


def test_patch_energy_certificate_invalid_efficiency_returns_422(
    client, editor_headers, sample_certificate
):
    response = client.patch(
        f"/energy-certificates/{sample_certificate.id}",
        json={"current_energy_efficiency": 120},
        headers=editor_headers,
    )
    assert response.status_code == 422


def test_delete_energy_certificate_then_get_returns_404(
    client, admin_headers, sample_certificate
):
    delete_response = client.delete(
        f"/energy-certificates/{sample_certificate.id}",
        headers=admin_headers,
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/energy-certificates/{sample_certificate.id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Energy certificate not found"

def test_editor_cannot_delete_energy_certificate(
    client, editor_headers, sample_certificate
):
    response = client.delete(
        f"/energy-certificates/{sample_certificate.id}",
        headers=editor_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions: admin role required"


def test_admin_can_delete_energy_certificate(
    client, admin_headers, sample_certificate
):
    response = client.delete(
        f"/energy-certificates/{sample_certificate.id}",
        headers=admin_headers,
    )
    assert response.status_code == 204


def test_delete_missing_energy_certificate_returns_404(client, admin_headers):
    response = client.delete("/energy-certificates/999999", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Energy certificate not found"

def test_filter_energy_certificates_for_property_with_no_certificates_returns_empty_list(
    client, sample_property
):
    response = client.get(f"/energy-certificates/?property_id={sample_property.id}")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_patch_energy_certificate_with_empty_body_returns_200_and_no_change(
    client, editor_headers, sample_certificate
):
    response = client.patch(
        f"/energy-certificates/{sample_certificate.id}",
        json={},
        headers=editor_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_certificate.id
    assert data["lmk_key"] == sample_certificate.lmk_key