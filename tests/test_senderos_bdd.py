import pytest
import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import given, when, then, parsers, scenarios

# Cargar todos los escenarios definidos en el archivo .feature
scenarios("../features/senderos_panama.feature")

MAX_SLA_SECONDS = 2.0


# -----------------------------------------------------------------------------
# DADO (GIVEN)
# -----------------------------------------------------------------------------


@pytest.fixture
def context():
    """Contenedor de estado compartido entre pasos de BDD."""
    return {}


@given(
    parsers.parse(
        'que elijo el sendero "{sendero}" con coordenadas latitud {latitud:f} y longitud {longitud:f}'
    )
)
def set_trail_coordinates(context, sendero, latitud, longitud):
    context["trail_name"] = sendero
    context["lat"] = latitud
    context["lon"] = longitud


@given(
    parsers.parse(
        "que configuro una coordenada inválida con latitud {latitud:f} y longitud {longitud:f}"
    )
)
def set_invalid_coordinates(context, latitud, longitud):
    context["lat"] = latitud
    context["lon"] = longitud


# -----------------------------------------------------------------------------
# CUANDO (WHEN)
# -----------------------------------------------------------------------------


@when("consulto el pronóstico del clima en Open-Meteo")
def get_weather_forecast(context, base_weather_url):
    params = {
        "latitude": context["lat"],
        "longitude": context["lon"],
        "current": "temperature_2m,relative_humidity_2m",
    }
    context["response"] = requests.get(base_weather_url, params=params, timeout=5)


@when("consulto el servicio de elevación de Open-Meteo")
def get_elevation(context, base_elevation_url):
    params = {
        "latitude": context["lat"],
        "longitude": context["lon"],
    }
    context["response"] = requests.get(base_elevation_url, params=params, timeout=5)


# -----------------------------------------------------------------------------
# ENTONCES (THEN)
# -----------------------------------------------------------------------------


@then(parsers.parse("la respuesta debe tener un código de estado {status_code:d}"))
def check_status_code(context, status_code):
    response = context["response"]
    assert (
        response.status_code == status_code
    ), f"Código de estado esperado: {status_code}, recibido: {response.status_code}. Detalle: {response.text}"


@then("el tiempo de respuesta debe ser menor a 2.0 segundos")
def check_response_time(context):
    elapsed = context["response"].elapsed.total_seconds()
    assert (
        elapsed < MAX_SLA_SECONDS
    ), f"El tiempo de respuesta fue de {elapsed}s (límite {MAX_SLA_SECONDS}s)"


@then("los datos deben incluir la temperatura actual y humedad relativa")
def check_weather_data(context):
    data = context["response"].json()
    assert "current" in data, "No se encontró el objeto 'current' en la respuesta JSON"
    current = data["current"]
    assert "temperature_2m" in current, "Falta la métrica 'temperature_2m'"
    assert "relative_humidity_2m" in current, "Falta la métrica 'relative_humidity_2m'"
    assert isinstance(current["temperature_2m"], (int, float))


@then(
    parsers.parse(
        "la elevación reportada debe estar dentro del rango de {elevacion_min} a {elevacion_max} msnm"
    )
)
def check_elevation_range(context, elevacion_min, elevacion_max):
    min_val = float(elevacion_min)
    max_val = float(elevacion_max)
    data = context["response"].json()
    assert (
        "elevation" in data
    ), "No se encontró el campo 'elevation' en la respuesta JSON"
    elev_val = (
        data["elevation"][0]
        if isinstance(data["elevation"], list)
        else data["elevation"]
    )
    assert (
        min_val <= elev_val <= max_val
    ), f"Elevación {elev_val} msnm fuera del rango esperado [{min_val}, {max_val}]"


@then("la respuesta debe indicar un error controlado con motivo descriptivo")
def check_error_payload(context):
    data = context["response"].json()
    assert data.get("error") is True, f"Se esperaba error=True, recibido: {data}"
    assert (
        "reason" in data and len(data["reason"]) > 0
    ), "Se esperaba un motivo 'reason' descriptivo"
