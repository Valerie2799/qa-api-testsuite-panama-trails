import pytest
import requests

# pyrefly: ignore [missing-import]
from pytest_bdd import when, then, parsers


def pytest_configure(config):
    """Registra marcadores personalizados del proyecto."""
    config.addinivalue_line(
        "markers",
        "posible_bug: Casos con discrepancias de elevación reportadas frente a datos de terreno, en investigación.",
    )
    config.addinivalue_line(
        "markers",
        "verificado: Casos con datos y respuestas verificadas frente a la API.",
    )


def pytest_collection_modifyitems(items):
    """Aplica xfail automáticamente a las pruebas marcadas con @posible_bug

    para mantener el pipeline verde mientras se investiga la discrepancia topográfica.
    """
    for item in items:
        if "posible_bug" in item.keywords:
            item.add_marker(
                pytest.mark.xfail(
                    reason=(
                        "Posible bug: Discrepancia entre la altura máxima esperada "
                        "(~950 msnm) y el valor devuelto por Open-Meteo. Pendiente "
                        "revisión con investigaciones de campo."
                    )
                )
            )


@pytest.fixture(scope="session")
def base_weather_url():
    """URL base para el endpoint de pronóstico de Open-Meteo."""
    return "https://api.open-meteo.com/v1/forecast"


@pytest.fixture(scope="session")
def base_elevation_url():
    """URL base para el endpoint de elevación de Open-Meteo."""
    return "https://api.open-meteo.com/v1/elevation"


@pytest.fixture(scope="session")
def panama_trails():
    """Datos geográficos y altitud de referencia para senderos de Panamá."""
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
# STEP DEFINITIONS COMPARTIDAS ENTRE senderos_panama.feature Y resiliencia_api.feature
# -----------------------------------------------------------------------------


@pytest.fixture
def context():
    """Contenedor de estado compartido entre pasos de BDD."""
    return {}


@when("consulto el pronóstico del clima en Open-Meteo")
def request_weather_forecast(context, base_weather_url):
    params = context.get("params", {})
    headers = context.get("headers", {})
    context["response"] = requests.get(
        base_weather_url, params=params, headers=headers, timeout=30
    )


@then(parsers.parse("la respuesta debe tener un código de estado {status_code:d}"))
def check_status_code(context, status_code):
    response = context["response"]
    assert (
        response.status_code == status_code
    ), f"Código de estado esperado: {status_code}, recibido: {response.status_code}. Detalle: {response.text}"
