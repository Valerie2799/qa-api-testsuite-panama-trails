# 📋 Plan de Proyecto: QA Test Suite - API Weather & Elevation (Senderos de Panamá)
> **Documento de Planificación y Alcance:** Automatización de pruebas de API REST para microclima y elevación geográfica en rutas de hiking en Panamá.

---

## 🎯 Visión General
Este proyecto demuestra el diseño e implementación de un marco de pruebas automatizadas (*API Testing*) sobre la API pública de **Open-Meteo**, evaluando la disponibilidad, precisión de datos y resiliencia de la interfaz para tres senderos emblemáticos de Panamá.

### 📍 Ubicación de los Senderos de Prueba
* **Volcán Barú (Chiriquí):** `Lat 8.8080, Long -82.5422` (~3,474 msnm).
* **Cerro Trinidad (Capira):** `Lat 8.7618, Long -79.9961` (~820 msnm).
* **La India Dormida (El Valle de Antón):** `Lat 8.6041, Long -80.1432` (~800 msnm).

---

## 🧪 Alcance de las Pruebas

1. **Pruebas Positivas (Happy Path - HTTP 200 OK):**
   * Endpoint `GET /v1/forecast`: Verificación de temperatura y probabilidad de lluvia en tiempo real.
   * Endpoint `GET /v1/elevation`: Verificación de la altitud en metros sobre el nivel del mar.
   * Validación del esquema JSON y tiempos de respuesta (< 2 segundos).

2. **Pruebas Negativas y Resiliencia:**
   * **HTTP 400 Bad Request:** Peticiones con coordenadas fuera de rango, tipos de datos inválidos o parámetros incompletos.
   * **Aclaratoria Caso HTTP 412 (Precondition Failed):** Evaluación de encabezados condicionales (`If-Match`); se documenta y valida que la API pública de Open-Meteo no implementa HTTP 412 por ser un servicio stateless de solo lectura (ignora precondiciones y responde 200 OK).

---

## 🤝 Marco de Delegación Humano - IA (1 Hora de Ejecución)

| Tiempo | Fase del Proyecto | Tareas Específicas | Responsable | Rol / Razón de Delegación |
| :---: | :--- | :--- | :---: | :--- |
| **00 - 10 min** | **1. Configuración del Entorno** | Crear carpeta, entorno virtual de Python (`venv`), instalar `pytest` / `requests` e inicializar Git. | **Tú (Humano)** | Tarea local de Sistemas que requiere permisos y control directo en tu máquina. |
| **10 - 25 min** | **2. Desarrollo de Pruebas Unitarias** | Escribir scripts en `pytest` parametrizados para los 3 senderos (200 OK), casos de error (400) y análisis de precondición (412). | **IA** | Acelera la generación de código base sintácticamente correcto y estructura la lógica de aserciones. |
| **25 - 40 min** | **3. Implementación BDD & Validación** | Redactar archivos `.feature` en Gherkin (`senderos_panama.feature`, `resiliencia_api.feature`), step definitions en `pytest-bdd`, etiquetar casos con `@posible_bug` y validar ejecución local. | **Colaborativo** | El humano aporta criterios de negocio y senderos; la IA conecta las definiciones de pasos y automatización. |
| **40 - 50 min** | **4. Pipeline de CI/CD** | Crear el archivo YAML de **GitHub Actions** para automatizar la ejecución en la nube en cada commit. | **IA** | Generación precisa de la sintaxis del pipeline de CI/CD sin errores de sangría en YAML. |
| **50 - 60 min** | **5. Documentación & Cierre** | Redactar el `README.md` del portafolio con insignias, arquitectura, plan del proyecto y contexto local de Panamá. | **Colaborativo** | La IA aporta el formato técnico profesional; tú agregas el contexto de negocio y el toque personal de hiking. |

---

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.x
* **Framework de Pruebas:** `pytest`
* **Librería HTTP:** `requests`
* **Integración Continua:** GitHub Actions
* **API Evaluada:** Open-Meteo REST API