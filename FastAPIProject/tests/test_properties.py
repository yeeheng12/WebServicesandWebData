def test_list_properties_returns_items_and_pagination(client, analytics_properties):
    response = client.get("/properties/")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["total"] >= 5
    assert len(data["items"]) >= 1


def test_filter_properties_by_town_city(client, analytics_properties):
    response = client.get("/properties/?town_city=Leeds")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 3
    assert all(item["town_city"] == "Leeds" for item in data["items"])


def test_filter_properties_by_postcode_case_insensitive(client, analytics_properties):
    response = client.get("/properties/?postcode=ls1%201aa")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 1
    assert data["items"][0]["postcode"] == "LS1 1AA"


def test_filter_properties_by_property_type(client, analytics_properties):
    response = client.get("/properties/?property_type=F")
    assert response.status_code == 200

    data = response.json()
    assert all(item["property_type"] == "F" for item in data["items"])


def test_filter_properties_by_price_range(client, analytics_properties):
    response = client.get("/properties/?min_price=200000&max_price=310000")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 3


def test_filter_properties_by_date_range(client, analytics_properties):
    response = client.get("/properties/?date_from=2024-01-01&date_to=2024-02-28")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 3


def test_filter_properties_by_epc_rating(client, analytics_properties):
    response = client.get("/properties/?epc_rating=B")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 1
    assert data["items"][0]["current_energy_rating"] == "B"


def test_filter_properties_by_efficiency_range(client, analytics_properties):
    response = client.get("/properties/?min_efficiency=70&max_efficiency=85")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 2


def test_sort_properties_by_price_ascending(client, analytics_properties):
    response = client.get("/properties/?sort_by=price&order=asc")
    assert response.status_code == 200

    items = response.json()["items"]
    prices = [item["price"] for item in items]
    assert prices == sorted(prices)


def test_sort_properties_by_sale_date_descending(client, analytics_properties):
    response = client.get("/properties/?sort_by=sale_date&order=desc")
    assert response.status_code == 200

    items = response.json()["items"]
    dates = [item["sale_date"] for item in items]
    assert dates == sorted(dates, reverse=True)


def test_pagination_metadata_is_correct(client, analytics_properties):
    response = client.get("/properties/?skip=1&limit=2")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["skip"] == 1
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["returned"] == 2
    assert data["pagination"]["total"] == 5
    assert data["pagination"]["has_previous"] is True


def test_invalid_price_range_returns_400(client):
    response = client.get("/properties/?min_price=500000&max_price=100000")
    assert response.status_code == 400
    assert response.json()["detail"] == "min_price cannot be greater than max_price"


def test_invalid_efficiency_range_returns_400(client):
    response = client.get("/properties/?min_efficiency=80&max_efficiency=50")
    assert response.status_code == 400
    assert response.json()["detail"] == "min_efficiency cannot be greater than max_efficiency"


def test_invalid_date_range_returns_400(client):
    response = client.get("/properties/?date_from=2024-12-01&date_to=2024-01-01")
    assert response.status_code == 400
    assert response.json()["detail"] == "date_from cannot be later than date_to"


def test_invalid_epc_rating_returns_400(client):
    response = client.get("/properties/?epc_rating=Z")
    assert response.status_code == 400
    assert response.json()["detail"] == "epc_rating must be one of: A, B, C, D, E, F, G"


def test_invalid_order_returns_400(client):
    response = client.get("/properties/?order=sideways")
    assert response.status_code == 400
    assert response.json()["detail"] == "order must be 'asc' or 'desc'"


def test_invalid_sort_field_returns_400(client):
    response = client.get("/properties/?sort_by=postcode")
    assert response.status_code == 400
    assert "sort_by must be one of" in response.json()["detail"]


def test_get_property_by_id_returns_links(client, sample_property):
    response = client.get(f"/properties/{sample_property.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_property.id
    assert "_links" in data
    assert data["_links"]["self"] == f"/properties/{sample_property.id}"
    assert data["_links"]["energy_certificates"] == f"/properties/{sample_property.id}/energy-certificates"


def test_get_missing_property_returns_404(client):
    response = client.get("/properties/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


def test_editor_can_create_property(client, editor_headers, property_payload):
    response = client.post("/properties/", json=property_payload, headers=editor_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["transaction_id"] == "txn-create-001"
    assert data["created_by_user_id"] is not None
    assert data["updated_by_user_id"] is not None


def test_create_property_duplicate_transaction_id_returns_409(
    client, editor_headers, property_payload
):
    response1 = client.post("/properties/", json=property_payload, headers=editor_headers)
    assert response1.status_code == 201

    response2 = client.post("/properties/", json=property_payload, headers=editor_headers)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "transaction_id already exists"


def test_create_property_invalid_price_returns_422(client, editor_headers, property_payload):
    payload = dict(property_payload)
    payload["price"] = -100

    response = client.post("/properties/", json=payload, headers=editor_headers)
    assert response.status_code == 422


def test_create_property_missing_required_price_returns_422(client, editor_headers, property_payload):
    payload = dict(property_payload)
    payload.pop("price")

    response = client.post("/properties/", json=payload, headers=editor_headers)
    assert response.status_code == 422


def test_editor_can_patch_property(client, editor_headers, sample_property):
    response = client.patch(
        f"/properties/{sample_property.id}",
        json={"price": 260000.0, "current_energy_rating": "B"},
        headers=editor_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["price"] == 260000.0
    assert data["current_energy_rating"] == "B"
    assert data["updated_by_user_id"] is not None


def test_patch_property_duplicate_transaction_id_returns_409(
    client, editor_headers, analytics_properties
):
    property_one = analytics_properties[0]
    property_two = analytics_properties[1]

    response = client.patch(
        f"/properties/{property_two.id}",
        json={"transaction_id": property_one.transaction_id},
        headers=editor_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "transaction_id already exists"


def test_patch_missing_property_returns_404(client, editor_headers):
    response = client.patch(
        "/properties/999999",
        json={"price": 123456.0},
        headers=editor_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


def test_admin_can_delete_property(client, admin_headers, sample_property):
    response = client.delete(f"/properties/{sample_property.id}", headers=admin_headers)
    assert response.status_code == 204

    follow_up = client.get(f"/properties/{sample_property.id}")
    assert follow_up.status_code == 404


def test_delete_missing_property_returns_404(client, admin_headers):
    response = client.delete("/properties/999999", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


def test_property_energy_certificates_returns_related_items(
    client, sample_property, sample_certificate
):
    response = client.get(f"/properties/{sample_property.id}/energy-certificates")
    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["property_id"] == sample_property.id


def test_property_energy_certificates_missing_property_returns_404(client):
    response = client.get("/properties/999999/energy-certificates")
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"

def test_properties_invalid_skip_returns_422_or_400(client, analytics_properties):
    response = client.get("/properties/?skip=-1")
    assert response.status_code in (400, 422)


def test_properties_invalid_limit_returns_422_or_400(client, analytics_properties):
    response = client.get("/properties/?limit=0")
    assert response.status_code in (400, 422)


def test_patch_property_invalid_rating_returns_422(
    client, editor_headers, sample_property
):
    response = client.patch(
        f"/properties/{sample_property.id}",
        json={"current_energy_rating": "Z"},
        headers=editor_headers,
    )
    assert response.status_code == 422

def test_filter_properties_unmatched_town_returns_empty_list(client):
    response = client.get("/properties/?town_city=NoSuchTownXYZ")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert data["items"] == []
    assert data["pagination"]["total"] == 0


def test_filter_properties_unmatched_postcode_returns_empty_list(client):
    response = client.get("/properties/?postcode=ZZ99ZZZ")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert data["items"] == []
    assert data["pagination"]["total"] == 0


def test_patch_property_with_empty_body_returns_200_and_no_change(
    client, editor_headers, sample_property
):
    original_price = sample_property.price

    response = client.patch(
        f"/properties/{sample_property.id}",
        json={},
        headers=editor_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_property.id
    assert data["price"] == original_price


def test_filter_properties_invalid_date_format_returns_422_or_400(client):
    response = client.get("/properties/?date_from=not-a-date")
    assert response.status_code in (400, 422)