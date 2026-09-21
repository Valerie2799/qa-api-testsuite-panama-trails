import pytest
import requests

MAX_RESPONSE_TIME_SECONDS = 2.0


class TestPanamaTrailsWeatherAndElevation:
    """Test suite to validate the Open-Meteo API on Panama trails."""

    # -------------------------------------------------------------------------
    # 1. POSITIVE TESTS (HAPPY PATH - HTTP 200 OK)
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "trail_name,lat,lon",
        [
            ("Volcán Barú (Chiriquí)", 8.8080, -82.5422),
            ("Cerro Trinidad (Capira)", 8.7618, -79.9961),
            ("La India Dormida (El Valle de Antón)", 8.6041, -80.1432),
        ],
    )
    def test_weather_forecast_happy_path(self, base_weather_url, trail_name, lat, lon):
        """Verifies that the forecast endpoint responds 200 OK in <2s with valid data."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m",
        }

        response = requests.get(base_weather_url, params=params, timeout=30)

        # 1. Status code validation
        assert (
            response.status_code == 200
        ), f"Error in {trail_name}: status {response.status_code}"

        # 2. Response time SLA validation (< 2 seconds)
        assert (
            response.elapsed.total_seconds() < MAX_RESPONSE_TIME_SECONDS
        ), f"{trail_name} took more than {MAX_RESPONSE_TIME_SECONDS}s: {response.elapsed.total_seconds()}s"

        # 3. JSON structure validation
        data = response.json()
        assert "current" in data, f"'current' object not found in {trail_name}"
        assert (
            "temperature_2m" in data["current"]
        ), f"Missing 'temperature_2m' in {trail_name}"
        assert isinstance(data["current"]["temperature_2m"], (int, float))

    @pytest.mark.parametrize(
        "trail_name,lat,lon,min_elev,max_elev",
        [
            ("Volcán Barú (Chiriquí)", 8.8080, -82.5422, 3300, 3550),
            pytest.param(
                "Cerro Trinidad (Capira)",
                8.7618,
                -79.9961,
                750,
                950,
                marks=pytest.mark.possible_bug,
            ),
            pytest.param(
                "La India Dormida (El Valle de Antón)",
                8.6041,
                -80.1432,
                700,
                900,
                marks=pytest.mark.possible_bug,
            ),
        ],
    )
    def test_elevation_happy_path(
        self, base_elevation_url, trail_name, lat, lon, min_elev, max_elev
    ):
        """Verifies that the elevation endpoint returns the expected altitude."""
        params = {"latitude": lat, "longitude": lon}

        response = requests.get(base_elevation_url, params=params, timeout=30)

        assert response.status_code == 200
        assert response.elapsed.total_seconds() < MAX_RESPONSE_TIME_SECONDS

        data = response.json()
        assert (
            "elevation" in data
        ), "The 'elevation' field was not found in the response"

        elevation_val = (
            data["elevation"][0]
            if isinstance(data["elevation"], list)
            else data["elevation"]
        )
        assert (
            min_elev <= elevation_val <= max_elev
        ), f"Unexpected elevation in {trail_name}: {elevation_val} masl (expected between {min_elev} and {max_elev})"

    # -------------------------------------------------------------------------
    # 2. NEGATIVE AND RESILIENCE TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "invalid_lat,invalid_lon,scenario",
        [
            (999.0, -82.5422, "Latitude out of global range (>90)"),
            (-95.0, -80.0, "Latitude out of lower range (<-90)"),
            (8.8080, 250.0, "Longitude out of upper range (>180)"),
            ("panama_city", -79.5, "Invalid data type (string instead of float)"),
        ],
    )
    def test_weather_negative_bad_request(
        self, base_weather_url, invalid_lat, invalid_lon, scenario
    ):
        """Verifies that the API returns HTTP 400 Bad Request for invalid parameters."""
        params = {"latitude": invalid_lat, "longitude": invalid_lon}

        response = requests.get(base_weather_url, params=params, timeout=30)

        assert (
            response.status_code == 400
        ), f"Expected 400 for '{scenario}', but received {response.status_code}"
        data = response.json()
        assert (
            data.get("error") is True
        ), f"Expected error=True in the body for '{scenario}'"
        assert (
            "reason" in data
        ), "Expected the 'reason' field with the error detail"

    def test_resilience_missing_mandatory_params(self, base_weather_url):
        """Verifies that omitting a mandatory parameter (e.g. latitude without longitude) returns HTTP 400 Bad Request."""
        params = {"latitude": 8.8080}
        response = requests.get(base_weather_url, params=params, timeout=30)
        assert response.status_code == 400
        data = response.json()
        assert data.get("error") is True
        assert "reason" in data

    def test_resilience_conditional_headers_not_supported(self, base_weather_url):
        """Clarification on HTTP 412: Open-Meteo is a public read-only API that does not implement
        conditional headers (If-Match / If-Unmodified-Since). It responds HTTP 200, ignoring
        the precondition instead of returning HTTP 412 Precondition Failed.
        """
        params = {
            "latitude": 8.8080,
            "longitude": -82.5422,
            "current": "temperature_2m",
        }
        headers = {"If-Match": '"nonexistent-etag-123"'}
        response = requests.get(
            base_weather_url, params=params, headers=headers, timeout=30
        )
        assert response.status_code == 200
