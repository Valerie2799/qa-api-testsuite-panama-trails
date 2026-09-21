import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import given, when, then, parsers, scenarios

# Load all scenarios defined in the .feature file
scenarios("../features/senderos_panama.feature")

MAX_SLA_SECONDS = 2.0


# -----------------------------------------------------------------------------
# GIVEN
# -----------------------------------------------------------------------------


@given(
    parsers.parse(
        'I choose the trail "{trail}" with coordinates latitude {latitude:f} and longitude {longitude:f}'
    )
)
def set_trail_coordinates(context, trail, latitude, longitude):
    context["trail_name"] = trail
    context["lat"] = latitude
    context["lon"] = longitude
    context["params"] = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m",
    }


# -----------------------------------------------------------------------------
# WHEN
# -----------------------------------------------------------------------------


@when("I query the Open-Meteo elevation service")
def get_elevation(context, base_elevation_url):
    params = {
        "latitude": context["lat"],
        "longitude": context["lon"],
    }
    context["response"] = requests.get(base_elevation_url, params=params, timeout=30)


# -----------------------------------------------------------------------------
# THEN
# -----------------------------------------------------------------------------


@then("the response time should be less than 2.0 seconds")
def check_response_time(context):
    elapsed = context["response"].elapsed.total_seconds()
    assert (
        elapsed < MAX_SLA_SECONDS
    ), f"Response time was {elapsed}s (limit {MAX_SLA_SECONDS}s)"


@then("the data should include the current temperature and relative humidity")
def check_weather_data(context):
    data = context["response"].json()
    assert "current" in data, "The 'current' object was not found in the JSON response"
    current = data["current"]
    assert "temperature_2m" in current, "Missing 'temperature_2m' metric"
    assert "relative_humidity_2m" in current, "Missing 'relative_humidity_2m' metric"
    assert isinstance(current["temperature_2m"], (int, float))


@then(
    parsers.parse(
        "the reported elevation should be within the range of {min_elevation} to {max_elevation} masl"
    )
)
def check_elevation_range(context, min_elevation, max_elevation):
    min_val = float(min_elevation)
    max_val = float(max_elevation)
    data = context["response"].json()
    assert (
        "elevation" in data
    ), "The 'elevation' field was not found in the JSON response"
    elev_val = (
        data["elevation"][0]
        if isinstance(data["elevation"], list)
        else data["elevation"]
    )
    assert (
        min_val <= elev_val <= max_val
    ), f"Elevation {elev_val} masl is outside the expected range [{min_val}, {max_val}]"
