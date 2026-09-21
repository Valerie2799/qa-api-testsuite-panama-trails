import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import given, when, then, parsers, scenarios

scenarios("../features/resiliencia_api.feature")


# -----------------------------------------------------------------------------
# GIVEN
# -----------------------------------------------------------------------------


@given(
    parsers.parse(
        "I configure an invalid coordinate with latitude {latitude:f} and longitude {longitude:f}"
    )
)
def set_invalid_coords(context, latitude, longitude):
    context["params"] = {"latitude": latitude, "longitude": longitude}


@given(
    parsers.parse(
        'I configure anomalous parameters with latitude "{latitude_str}" and longitude "{longitude_str}"'
    )
)
def set_string_coords(context, latitude_str, longitude_str):
    context["params"] = {"latitude": latitude_str, "longitude": longitude_str}


@given(
    parsers.parse(
        'I configure a request with only the latitude parameter "{latitude}" and no longitude'
    )
)
def set_missing_param(context, latitude):
    context["params"] = {"latitude": latitude}


@given(
    parsers.parse(
        'I configure a valid request for Volcán Barú with conditional header "{header_name}"'
    )
)
def set_conditional_header(context, header_name):
    context["params"] = {
        "latitude": 8.8080,
        "longitude": -82.5422,
        "current": "temperature_2m",
    }
    context["headers"] = {header_name: '"test-etag-invalid"'}


# -----------------------------------------------------------------------------
# WHEN
# -----------------------------------------------------------------------------


@when("I query the weather forecast with text parameters")
@when("I query the weather forecast with incomplete parameters")
def execute_weather_call(context, base_weather_url):
    params = context.get("params", {})
    headers = context.get("headers", {})
    context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


@when("I query the weather forecast with conditional headers")
def execute_conditional_call(context, base_weather_url):
    params = context.get("params", {})
    headers = context.get("headers", {})
    context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


# -----------------------------------------------------------------------------
# THEN
# -----------------------------------------------------------------------------


@then("the response should indicate a controlled error with a descriptive reason")
def check_error_details(context):
    data = context["response"].json()
    assert data.get("error") is True, f"Expected error=True, but received: {data}"
    assert (
        "reason" in data and len(data["reason"]) > 0
    ), "Expected a descriptive 'reason' in the response JSON"


@then(
    "it is confirmed that the public API does not implement HTTP 412 since it is a stateless read-only service"
)
def verify_no_412_reason(context):
    response = context["response"]
    # Open-Meteo processes the request as 200 OK and ignores If-Match / If-Unmodified-Since
    assert (
        response.status_code == 200
    ), f"Expected 200 OK for conditional header, but got {response.status_code}"
