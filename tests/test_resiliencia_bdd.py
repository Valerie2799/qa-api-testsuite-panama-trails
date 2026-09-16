import pytest
import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import given, when, then, parsers, scenarios

scenarios("../features/resiliencia_api.feature")


@pytest.fixture
def res_context():
    """Contenedor de estado compartido para las pruebas de resiliencia BDD."""
    return {}


# -----------------------------------------------------------------------------
# DADO (GIVEN)
# -----------------------------------------------------------------------------


@given(
    parsers.parse(
        "que configuro una coordenada inválida con latitud {latitud:f} y longitud {longitud:f}"
    )
)
def set_invalid_coords(res_context, latitud, longitud):
    res_context["params"] = {"latitude": latitud, "longitude": longitud}


@given(
    parsers.parse(
        'que configuro parámetros anómalos con latitud "{latitud_str}" y longitud "{longitud_str}"'
    )
)
def set_string_coords(res_context, latitud_str, longitud_str):
    res_context["params"] = {"latitude": latitud_str, "longitude": longitud_str}


@given(
    parsers.parse(
        'que configuro una petición con solo el parámetro latitud "{latitud}" sin longitud'
    )
)
def set_missing_param(res_context, latitud):
    res_context["params"] = {"latitude": latitud}


@given(
    parsers.parse(
        'que configuro una petición válida para el Volcán Barú con encabezado condicional "{header_name}"'
    )
)
def set_conditional_header(res_context, header_name):
    res_context["params"] = {
        "latitude": 8.8080,
        "longitude": -82.5422,
        "current": "temperature_2m",
    }
    res_context["headers"] = {header_name: '"etag-de-prueba-invalido"'}


# -----------------------------------------------------------------------------
# CUANDO (WHEN)
# -----------------------------------------------------------------------------


@when("consulto el pronóstico del clima en Open-Meteo")
@when("consulto el pronóstico del clima con parámetros de texto")
@when("consulto el pronóstico del clima con parámetros incompletos")
def execute_weather_call(res_context, base_weather_url):
    params = res_context.get("params", {})
    headers = res_context.get("headers", {})
    res_context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


@when("consulto el pronóstico del clima con encabezados condicionales")
def execute_conditional_call(res_context, base_weather_url):
    params = res_context.get("params", {})
    headers = res_context.get("headers", {})
    res_context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


# -----------------------------------------------------------------------------
# ENTONCES (THEN)
# -----------------------------------------------------------------------------


@then(parsers.parse("la respuesta debe tener un código de estado {status_code:d}"))
def check_status_code(res_context, status_code):
    response = res_context["response"]
    assert (
        response.status_code == status_code
    ), f"Código de estado esperado: {status_code}, recibido: {response.status_code}. Detalle: {response.text}"


@then("la respuesta debe indicar un error controlado con motivo descriptivo")
def check_error_details(res_context):
    data = res_context["response"].json()
    assert data.get("error") is True, f"Se esperaba error=True, pero se recibió: {data}"
    assert (
        "reason" in data and len(data["reason"]) > 0
    ), "Se esperaba un motivo 'reason' descriptivo en el JSON de respuesta"


@then(
    "se confirma que la API pública no implementa HTTP 412 por ser un servicio de solo lectura sin estado"
)
def verify_no_412_reason(res_context):
    response = res_context["response"]
    # Open-Meteo procesa la solicitud como 200 OK e ignora If-Match / If-Unmodified-Since
    assert (
        response.status_code == 200
    ), f"Se esperaba 200 OK ante encabezado condicional, pero se obtuvo {response.status_code}"
