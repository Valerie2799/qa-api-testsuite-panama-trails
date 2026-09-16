import pytest
import requests

MAX_RESPONSE_TIME_SECONDS = 2.0


class TestPanamaTrailsWeatherAndElevation:
    """Suite de pruebas para validar la API de Open-Meteo en senderos de Panamá."""

    # -------------------------------------------------------------------------
    # 1. PRUEBAS POSITIVAS (HAPPY PATH - HTTP 200 OK)
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
        """Verifica que el endpoint de pronóstico responda 200 OK en <2s con datos válidos."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m",
        }

        response = requests.get(base_weather_url, params=params, timeout=5)

        # 1. Validación de código de estado
        assert (
            response.status_code == 200
        ), f"Error en {trail_name}: status {response.status_code}"

        # 2. Validación de SLA de tiempo de respuesta (< 2 segundos)
        assert (
            response.elapsed.total_seconds() < MAX_RESPONSE_TIME_SECONDS
        ), f"{trail_name} tardó más de {MAX_RESPONSE_TIME_SECONDS}s: {response.elapsed.total_seconds()}s"

        # 3. Validación de estructura JSON
        data = response.json()
        assert "current" in data, f"No se encontró el objeto 'current' en {trail_name}"
        assert (
            "temperature_2m" in data["current"]
        ), f"Falta 'temperature_2m' en {trail_name}"
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
                marks=pytest.mark.posible_bug,
            ),
            pytest.param(
                "La India Dormida (El Valle de Antón)",
                8.6041,
                -80.1432,
                700,
                900,
                marks=pytest.mark.posible_bug,
            ),
        ],
    )
    def test_elevation_happy_path(
        self, base_elevation_url, trail_name, lat, lon, min_elev, max_elev
    ):
        """Verifica que el endpoint de elevación devuelva la altitud esperada."""
        params = {"latitude": lat, "longitude": lon}

        response = requests.get(base_elevation_url, params=params, timeout=5)

        assert response.status_code == 200
        assert response.elapsed.total_seconds() < MAX_RESPONSE_TIME_SECONDS

        data = response.json()
        assert (
            "elevation" in data
        ), "No se encontró el campo 'elevation' en la respuesta"

        elevation_val = (
            data["elevation"][0]
            if isinstance(data["elevation"], list)
            else data["elevation"]
        )
        assert (
            min_elev <= elevation_val <= max_elev
        ), f"Elevación inesperada en {trail_name}: {elevation_val} msnm (esperado entre {min_elev} y {max_elev})"

    # -------------------------------------------------------------------------
    # 2. PRUEBAS NEGATIVAS Y RESILIENCIA
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "invalid_lat,invalid_lon,scenario",
        [
            (999.0, -82.5422, "Latitud fuera de rango global (>90)"),
            (-95.0, -80.0, "Latitud fuera de rango inferior (<-90)"),
            (8.8080, 250.0, "Longitud fuera de rango superior (>180)"),
            ("panama_city", -79.5, "Tipo de dato inválido (string en lugar de float)"),
        ],
    )
    def test_weather_negative_bad_request(
        self, base_weather_url, invalid_lat, invalid_lon, scenario
    ):
        """Verifica que la API retorne HTTP 400 Bad Request ante parámetros no válidos."""
        params = {"latitude": invalid_lat, "longitude": invalid_lon}

        response = requests.get(base_weather_url, params=params, timeout=5)

        assert (
            response.status_code == 400
        ), f"Esperado 400 para '{scenario}', pero se recibió {response.status_code}"
        data = response.json()
        assert (
            data.get("error") is True
        ), f"Se esperaba error=True en el cuerpo para '{scenario}'"
        assert (
            "reason" in data
        ), "Se esperaba el campo 'reason' con el detalle del error"

    def test_resilience_missing_mandatory_params(self, base_weather_url):
        """Verifica que omitir un parámetro mandatorio (ej. latitud sin longitud) retorne HTTP 400 Bad Request."""
        params = {"latitude": 8.8080}
        response = requests.get(base_weather_url, params=params, timeout=5)
        assert response.status_code == 400
        data = response.json()
        assert data.get("error") is True
        assert "reason" in data

    def test_resilience_conditional_headers_not_supported(self, base_weather_url):
        """Aclaratoria HTTP 412: Open-Meteo es una API pública de solo lectura que no implementa
        encabezados condicionales (If-Match / If-Unmodified-Since). Responde HTTP 200 ignorando
        la precondición en lugar de generar HTTP 412 Precondition Failed.
        """
        params = {
            "latitude": 8.8080,
            "longitude": -82.5422,
            "current": "temperature_2m",
        }
        headers = {"If-Match": '"etag-inexistente-123"'}
        response = requests.get(
            base_weather_url, params=params, headers=headers, timeout=5
        )
        assert response.status_code == 200
