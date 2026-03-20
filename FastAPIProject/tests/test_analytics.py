def test_average_price_all_properties(client, analytics_properties):
    response = client.get("/analytics/average-price")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 5
    assert data["average_price"] == 272000.0


def test_average_price_for_area(client, analytics_properties):
    response = client.get("/analytics/average-price?area=Leeds")
    assert response.status_code == 200

    data = response.json()
    assert data["area"] == "Leeds"
    assert data["count"] == 3
    assert data["average_price"] == 253333.33


def test_average_price_missing_area_returns_404(client):
    response = client.get("/analytics/average-price?area=Nowhere")
    assert response.status_code == 404
    assert response.json()["detail"] == "No matching properties found"


def test_median_price_for_area(client, analytics_properties):
    response = client.get("/analytics/median-price?area=Leeds")
    assert response.status_code == 200

    data = response.json()
    assert data["median_price"] == 250000.0
    assert data["count"] == 3


def test_price_by_property_type_returns_grouped_results(client, analytics_properties):
    response = client.get("/analytics/price-by-property-type")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(item["property_type"] == "F" for item in data)


def test_epc_distribution_returns_grouped_results(client, analytics_properties):
    response = client.get("/analytics/epc-distribution")
    assert response.status_code == 200

    data = response.json()
    ratings = {item["current_energy_rating"] for item in data}
    assert {"A", "B", "C", "E", "F"} <= ratings


def test_efficiency_summary_for_area(client, analytics_properties):
    response = client.get("/analytics/efficiency-summary?area=Leeds")
    assert response.status_code == 200

    data = response.json()
    assert data["area"] == "Leeds"
    assert data["count"] == 3
    assert data["average_current_efficiency"] == 69.67
    assert data["average_potential_efficiency"] == 81.33


def test_price_vs_efficiency_returns_grouped_results(client, analytics_properties):
    response = client.get("/analytics/price-vs-efficiency")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(item["current_energy_rating"] == "A" for item in data)
    assert any(item["current_energy_rating"] == "F" for item in data)


def test_compare_locations_success(client, analytics_properties):
    response = client.get("/analytics/compare-locations?area1=Leeds&area2=Manchester")
    assert response.status_code == 200

    data = response.json()
    assert data["area1"] == "Leeds"
    assert data["area2"] == "Manchester"
    assert data["area1_count"] == 3
    assert data["area2_count"] == 1


def test_compare_locations_missing_area_returns_404(client, analytics_properties):
    response = client.get("/analytics/compare-locations?area1=Leeds&area2=Nowhere")
    assert response.status_code == 404
    assert response.json()["detail"] == "One or both locations not found"


def test_price_trend_by_year(client, analytics_properties):
    response = client.get("/analytics/price-trend?interval=year")
    assert response.status_code == 200

    data = response.json()
    periods = [item["period"] for item in data]
    assert "2023" in periods
    assert "2024" in periods


def test_price_trend_by_month_for_area(client, analytics_properties):
    response = client.get("/analytics/price-trend?interval=month&area=Leeds")
    assert response.status_code == 200

    data = response.json()
    periods = [item["period"] for item in data]
    assert "2024-01" in periods
    assert "2024-02" in periods


def test_energy_price_impact_for_area(client, analytics_properties):
    response = client.get("/analytics/energy-price-impact?area=Leeds")
    assert response.status_code == 200

    data = response.json()
    assert data["area"] == "Leeds"
    assert data["high_efficiency_count"] == 2
    assert data["low_efficiency_count"] == 1
    assert data["high_efficiency_average_price"] == 275000.0
    assert data["low_efficiency_average_price"] == 210000.0
    assert data["price_difference"] == 65000.0
    assert data["percentage_difference"] == 30.95


def test_energy_price_impact_missing_area_returns_404(client):
    response = client.get("/analytics/energy-price-impact?area=Nowhere")
    assert response.status_code == 404
    assert response.json()["detail"] == "No matching properties found"


def test_top_areas_by_price_respects_limit(client, analytics_properties):
    response = client.get("/analytics/top-areas-by-price?limit=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["average_price"] >= data[1]["average_price"]


def test_top_areas_by_energy_premium_returns_ranked_results(client, analytics_properties):
    response = client.get("/analytics/top-areas-by-energy-premium")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["area_name"] == "Leeds"


def test_sales_volume_trend_by_year(client, analytics_properties):
    response = client.get("/analytics/sales-volume-trend?interval=year")
    assert response.status_code == 200

    data = response.json()
    assert any(item["period"] == "2023" for item in data)
    assert any(item["period"] == "2024" for item in data)


def test_sales_volume_trend_by_month_for_area(client, analytics_properties):
    response = client.get("/analytics/sales-volume-trend?interval=month&area=Leeds")
    assert response.status_code == 200

    data = response.json()
    periods = [item["period"] for item in data]
    assert "2024-01" in periods
    assert "2024-02" in periods

def test_compare_locations_missing_second_area_returns_422_or_400(client):
    response = client.get("/analytics/compare-locations?area1=Leeds")
    assert response.status_code in (400, 422)


def test_top_areas_by_price_invalid_limit_returns_422_or_400(client):
    response = client.get("/analytics/top-areas-by-price?limit=0")
    assert response.status_code in (400, 422)


def test_price_trend_invalid_interval_returns_422_or_400(client):
    response = client.get("/analytics/price-trend?interval=weekly")
    assert response.status_code in (400, 422)


def test_sales_volume_trend_invalid_interval_returns_422_or_400(client):
    response = client.get("/analytics/sales-volume-trend?interval=weekly")
    assert response.status_code in (400, 422)