# 🏔️ QA Test Suite - API Weather & Elevation (Senderos de Panamá)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![BDD Gherkin](https://img.shields.io/badge/BDD-Gherkin%20%2F%20pytest--bdd-brightgreen.svg)
![Pytest](https://img.shields.io/badge/Tested%20with-Pytest-0A9EDC.svg)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)
![Status](https://img.shields.io/badge/Tests-Passing-success.svg)

Suite automatizada de pruebas de API REST utilizando **Behavior-Driven Development (BDD)** con **Gherkin** y **pytest-bdd**. El proyecto evalúa la disponibilidad, tiempos de respuesta (<2s), precisión geográfica y resiliencia de la API pública de **Open-Meteo**, contextualizada en tres de las rutas de senderismo y montaña más emblemáticas de Panamá.

---

## 📖 Enfoque BDD (Behavior-Driven Development)

El comportamiento y los objetivos de negocio de las pruebas están especificados en lenguaje natural ubicuo en [`features/senderos_panama.feature`](features/senderos_panama.feature):

* **Escenario 1 (Happy Path - Clima):** Consulta de temperatura actual y humedad relativa en los senderos.
* **Escenario 2 (Happy Path - Elevación):** Validación de altitud en metros sobre el nivel del mar (msnm).
* **Escenario 3 (Negative Path - Resiliencia):** Manejo controlado de códigos de error HTTP 400 ante coordenadas no válidas.

---

## 📍 Senderos Evaluados

| Sendero | Provincia | Coordenadas | Altitud Esperada |
| :--- | :--- | :--- | :--- |
| **Volcán Barú** | Chiriquí | `8.8080 N, -82.5422 W` | ~3,474 msnm (3300 - 3550 msnm) |
| **Cerro Trinidad** | Capira (Panamá Oeste) | `8.7618 N, -79.9961 W` | ~820 msnm (750 - 950 msnm) |
| **La India Dormida** | Coclé (El Valle de Antón) | `8.6041 N, -80.1432 W` | ~800 msnm (700 - 900 msnm) |

---

## 📁 Estructura del Repositorio

```text
AI-FLUENCY/
├── .github/
│   └── workflows/
│       └── test.yml                 # Pipeline automatizado de CI/CD
├── features/
│   └── senderos_panama.feature      # Especificación BDD en Gherkin (español)
├── tests/
│   ├── conftest.py                  # Fixtures compartidas de pytest
│   ├── test_senderos_bdd.py         # Definición de pasos BDD (pytest-bdd)
│   └── test_weather_elevation.py    # Suite de pruebas unitarias/integración directa
├── PROJECT_PLAN.md                  # Plan y alcance del proyecto (Matriz Humano-IA)
├── requirements.txt                 # Dependencias del proyecto
└── README.md                        # Documentación técnica
```

> 📋 **Plan del Proyecto:** Para consultar el plan original de ejecución, alcance y matriz de colaboración Humano-IA, revisa el archivo [`PROJECT_PLAN.md`](PROJECT_PLAN.md).

---

## 🚀 Ejecución Local

### 1. Clonar y preparar entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows PowerShell
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar la suite BDD
```bash
# Ejecutar únicamente los escenarios BDD con salida detallada
pytest tests/test_senderos_bdd.py -v

# O ejecutar toda la suite (BDD + pruebas directas)
pytest tests/ -v
```

---

## ⚙️ Integración Continua (CI/CD)
El pipeline en `.github/workflows/test.yml` se ejecuta automáticamente ante cada `push` o `pull_request` a las ramas `main` o `master`, instalando las dependencias y validando tanto los escenarios BDD como las pruebas unitarias.

### ⚠️ Limitación conocida: rate-limiting de la API pública gratuita
Open-Meteo es una API pública y gratuita, y sus rangos de IP compartidos con miles de pipelines de GitHub Actions en todo el mundo pueden recibir *throttling* cuando reciben ráfagas de solicitudes. Esto puede provocar `ReadTimeout` intermitentes en el runner de CI que **no reflejan un defecto en la aplicación bajo prueba ni en la suite**. Para mitigarlo:
* Se espacian las solicitudes con una breve pausa entre pruebas (`throttle_open_meteo_requests` en `conftest.py`).
* Se configuran reintentos automáticos limitados a errores de red transitorios (`pytest-rerunfailures`, solo para `ReadTimeout`/`ConnectionError`, nunca para fallos de aserción).

Si el pipeline falla en CI pero la suite pasa en local, es indicativo de este límite externo, no de una regresión.

---

## 📋 Declaración de Diligencia

En el desarrollo de este proyecto se utilizó Claude (Anthropic) como asistente en la redacción de step definitions BDD, la configuración de CI/CD y la resolución de fallos transitorios de red. No se empleó información sensible; el proyecto consume únicamente APIs públicas. Todo el código generado fue sometido a revisión mediante ejecución de pruebas y code review antes de su incorporación. La autora asume responsabilidad total por el resultado final, su exactitud y su presentación.
