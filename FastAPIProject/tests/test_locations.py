def test_list_locations_returns_distinct_names(client, analytics_properties):
    response = client.get("/locations/")
    assert response.status_code == 200

    data = response.json()
    assert "Leeds" in data
    assert "Manchester" in data
    assert "Bristol" in data


def test_location_summary_returns_expected_shape(client, analytics_properties):
    response = client.get("/locations/Leeds/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["location_name"] == "Leeds"
    assert data["listing_count"] == 3
    assert "average_price" in data
    assert "median_price" in data
    assert "average_efficiency" in data
    assert "average_floor_area" in data
    assert "_links" in data


def test_location_summary_contains_hateoas_links(client, analytics_properties):
    response = client.get("/locations/Leeds/summary")
    assert response.status_code == 200

    links = response.json()["_links"]
    assert links["self"] == "/locations/Leeds/summary"
    assert links["related_area_properties"] == "/properties/?town_city=Leeds"
    assert links["price_trend"] == "/analytics/price-trend?area_type=town_city&area=Leeds"
    assert links["energy_price_impact"] == "/analytics/energy-price-impact?area_type=town_city&area=Leeds"


def test_location_summary_missing_location_returns_404(client):
    response = client.get("/locations/Nowhere/summary")
    assert response.status_code == 404
    assert response.json()["detail"] == "Location not found"