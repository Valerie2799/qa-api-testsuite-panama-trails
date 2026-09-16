# language: es
Característica: Pruebas de resiliencia y límites de protocolo en la API de Open-Meteo
  Como integrador de software
  Quiero comprobar cómo responde la API ante peticiones anómalas, parámetros incompletos y encabezados
  Para validar la robustez, mensajes de error controlados y comportamiento de la API

  Esquema del escenario: Validación ante coordenadas fuera del rango geográfico admisible
    Dado que configuro una coordenada inválida con latitud <latitud> y longitud <longitud>
    Cuando consulto el pronóstico del clima en Open-Meteo
    Entonces la respuesta debe tener un código de estado 400
    Y la respuesta debe indicar un error controlado con motivo descriptivo

    Ejemplos:
      | latitud | longitud | motivo                       |
      |   999.0 | -82.5422 | Latitud mayor a 90 grados    |
      |   -95.0 |    -80.0 | Latitud menor a -90 grados   |
      |  8.8080 |    250.0 | Longitud mayor a 180 grados  |
      |  8.8080 |   -250.0 | Longitud menor a -180 grados |

  Esquema del escenario: Validación ante tipos de datos no numéricos
    Dado que configuro parámetros anómalos con latitud "<latitud_str>" y longitud "<longitud_str>"
    Cuando consulto el pronóstico del clima con parámetros de texto
    Entonces la respuesta debe tener un código de estado 400
    Y la respuesta debe indicar un error controlado con motivo descriptivo

    Ejemplos:
      | latitud_str | longitud_str | motivo                     |
      | panama_city |        -79.5 | Texto en lugar de latitud  |
      |      8.8080 | invalido     | Texto en lugar de longitud |

  Escenario: Manejo de petición con parámetro obligatorio faltante (latitud sin longitud)
    Dado que configuro una petición con solo el parámetro latitud "8.8080" sin longitud
    Cuando consulto el pronóstico del clima con parámetros incompletos
    Entonces la respuesta debe tener un código de estado 400
    Y la respuesta debe indicar un error controlado con motivo descriptivo

  Escenario: Evaluación de encabezados condicionales (Aclaratoria caso HTTP 412 no soportado)
    Dado que configuro una petición válida para el Volcán Barú con encabezado condicional "If-Match"
    Cuando consulto el pronóstico del clima con encabezados condicionales
    Entonces la respuesta debe tener un código de estado 200
    Y se confirma que la API pública no implementa HTTP 412 por ser un servicio de solo lectura sin estado
