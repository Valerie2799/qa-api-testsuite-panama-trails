# language: es
Característica: Validación de microclima y elevación geográfica en senderos de Panamá
  Como senderista
  Quiero consultar el estado del clima y la elevación del sendero al que deseo ir
  Para poder prepararme a las condiciones climáticas y del terreno antes de iniciar la excursión

  Esquema del escenario: Como senderista quiero consultar las condiciones meteorológicas actuales del sendero
    Dado que elijo el sendero "<sendero>" con coordenadas latitud <latitud> y longitud <longitud>
    Cuando consulto el pronóstico del clima en Open-Meteo
    Entonces la respuesta debe tener un código de estado 200
    Y el tiempo de respuesta debe ser menor a 2.0 segundos
    Y los datos deben incluir la temperatura actual y humedad relativa

    Ejemplos:
      | sendero                              | latitud | longitud |
      | Volcán Barú (Chiriquí)               |  8.8080 | -82.5422 |
      | Cerro Trinidad (Capira)              |  8.7618 | -79.9961 |
      | La India Dormida (El Valle de Antón) |  8.6041 | -80.1432 |

  @verificado
  Esquema del escenario: Como senderista quiero verificar la elevación del sendero confirmado
    Dado que elijo el sendero "<sendero>" con coordenadas latitud <latitud> y longitud <longitud>
    Cuando consulto el servicio de elevación de Open-Meteo
    Entonces la respuesta debe tener un código de estado 200
    Y el tiempo de respuesta debe ser menor a 2.0 segundos
    Y la elevación reportada debe estar dentro del rango de <elevacion_min> a <elevacion_max> msnm

    Ejemplos:
      | sendero                | latitud | longitud | elevacion_min | elevacion_max |
      | Volcán Barú (Chiriquí) |  8.8080 | -82.5422 |          3300 |          3550 |

  @posible_bug
  Esquema del escenario: Como senderista quiero verificar la elevación de senderos en investigación
    # NOTA: Cerro Trinidad (altura máx ~950 msnm) y La India Dormida (~800-900 msnm) presentan
    # discrepancia con la altitud devuelta por Open-Meteo (224 msnm y 588 msnm) en estas coordenadas.
    # Se etiqueta con @posible_bug para contrastar con investigaciones de campo y modelos topográficos.
    Dado que elijo el sendero "<sendero>" con coordenadas latitud <latitud> y longitud <longitud>
    Cuando consulto el servicio de elevación de Open-Meteo
    Entonces la respuesta debe tener un código de estado 200
    Y el tiempo de respuesta debe ser menor a 2.0 segundos
    Y la elevación reportada debe estar dentro del rango de <elevacion_min> a <elevacion_max> msnm

    Ejemplos:
      | sendero                              | latitud | longitud | elevacion_min | elevacion_max |
      | Cerro Trinidad (Capira)              |  8.7618 | -79.9961 |           750 |           950 |
      | La India Dormida (El Valle de Antón) |  8.6041 | -80.1432 |           700 |           900 |
