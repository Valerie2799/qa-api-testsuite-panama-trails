import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import given, when, then, parsers, scenarios

scenarios("../features/resiliencia_api.feature")


# -----------------------------------------------------------------------------
# DADO (GIVEN)
# -----------------------------------------------------------------------------


@given(
    parsers.parse(
        "que configuro una coordenada inválida con latitud {latitud:f} y longitud {longitud:f}"
    )
)
def set_invalid_coords(context, latitud, longitud):
    context["params"] = {"latitude": latitud, "longitude": longitud}


@given(
    parsers.parse(
        'que configuro parámetros anómalos con latitud "{latitud_str}" y longitud "{longitud_str}"'
    )
)
def set_string_coords(context, latitud_str, longitud_str):
    context["params"] = {"latitude": latitud_str, "longitude": longitud_str}


@given(
    parsers.parse(
        'que configuro una petición con solo el parámetro latitud "{latitud}" sin longitud'
    )
)
def set_missing_param(context, latitud):
    context["params"] = {"latitude": latitud}


@given(
    parsers.parse(
        'que configuro una petición válida para el Volcán Barú con encabezado condicional "{header_name}"'
    )
)
def set_conditional_header(context, header_name):
    context["params"] = {
        "latitude": 8.8080,
        "longitude": -82.5422,
        "current": "temperature_2m",
    }
    context["headers"] = {header_name: '"etag-de-prueba-invalido"'}


# -----------------------------------------------------------------------------
# CUANDO (WHEN)
# -----------------------------------------------------------------------------


@when("consulto el pronóstico del clima con parámetros de texto")
@when("consulto el pronóstico del clima con parámetros incompletos")
def execute_weather_call(context, base_weather_url):
    params = context.get("params", {})
    headers = context.get("headers", {})
    context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


@when("consulto el pronóstico del clima con encabezados condicionales")
def execute_conditional_call(context, base_weather_url):
    params = context.get("params", {})
    headers = context.get("headers", {})
    context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


# -----------------------------------------------------------------------------
# ENTONCES (THEN)
# -----------------------------------------------------------------------------


@then("la respuesta debe indicar un error controlado con motivo descriptivo")
def check_error_details(context):
    data = context["response"].json()
    assert data.get("error") is True, f"Se esperaba error=True, pero se recibió: {data}"
    assert (
        "reason" in data and len(data["reason"]) > 0
    ), "Se esperaba un motivo 'reason' descriptivo en el JSON de respuesta"


@then(
    "se confirma que la API pública no implementa HTTP 412 por ser un servicio de solo lectura sin estado"
)
def verify_no_412_reason(context):
    response = context["response"]
    # Open-Meteo procesa la solicitud como 200 OK e ignora If-Match / If-Unmodified-Since
    assert (
        response.status_code == 200
    ), f"Se esperaba 200 OK ante encabezado condicional, pero se obtuvo {response.status_code}"
