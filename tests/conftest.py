import time

import pytest
import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import when, then, parsers

REQUEST_THROTTLE_SECONDS = 1.5


def pytest_configure(config):
    """Registers the project's custom markers."""
    config.addinivalue_line(
        "markers",
        "possible_bug: Cases with elevation discrepancies reported against terrain data, under investigation.",
    )
    config.addinivalue_line(
        "markers",
        "verified: Cases with data and responses verified against the API.",
    )


def pytest_collection_modifyitems(items):
    """Automatically applies xfail to tests marked with @possible_bug

    to keep the pipeline green while the topographic discrepancy is investigated.
    """
    for item in items:
        if "possible_bug" in item.keywords:
            item.add_marker(
                pytest.mark.xfail(
                    reason=(
                        "Possible bug: Discrepancy between the expected maximum height "
                        "(~950 masl) and the value returned by Open-Meteo. Pending "
                        "review with field surveys."
                    )
                )
            )


@pytest.fixture(scope="session")
def base_weather_url():
    """Base URL for the Open-Meteo forecast endpoint."""
    return "https://api.open-meteo.com/v1/forecast"


@pytest.fixture(scope="session")
def base_elevation_url():
    """Base URL for the Open-Meteo elevation endpoint."""
    return "https://api.open-meteo.com/v1/elevation"


@pytest.fixture(autouse=True)
def throttle_open_meteo_requests():
    """Spaces out requests to the public API to avoid the rate-limiting

    that Open-Meteo applies to shared IP ranges such as GitHub Actions
    runners when they receive bursts of consecutive requests.
    """
    yield
    time.sleep(REQUEST_THROTTLE_SECONDS)


@pytest.fixture(scope="session")
def panama_trails():
    """Geographic and reference elevation data for Panama trails."""
    return [
        {
            "name": "Volcán Barú (Chiriquí)",
            "lat": 8.8080,
            "lon": -82.5422,
            "expected_elevation_min": 3300,
            "expected_elevation_max": 3550,
        },
        {
            "name": "Cerro Trinidad (Capira)",
            "lat": 8.7618,
            "lon": -79.9961,
            "expected_elevation_min": 750,
            "expected_elevation_max": 950,
        },
        {
            "name": "La India Dormida (El Valle de Antón)",
            "lat": 8.6041,
            "lon": -80.1432,
            "expected_elevation_min": 700,
            "expected_elevation_max": 900,
        },
    ]


# -----------------------------------------------------------------------------
# STEP DEFINITIONS SHARED BETWEEN senderos_panama.feature AND resiliencia_api.feature
# -----------------------------------------------------------------------------


@pytest.fixture
def context():
    """Shared state container between BDD steps."""
    return {}


@when("I query the weather forecast on Open-Meteo")
def request_weather_forecast(context, base_weather_url):
    params = context.get("params", {})
    headers = context.get("headers", {})
    context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


@then(parsers.parse("the response should have a {status_code:d} status code"))
def check_status_code(context, status_code):
    response = context["response"]
    assert (
        response.status_code == status_code
    ), f"Expected status code: {status_code}, received: {response.status_code}. Detail: {response.text}"
