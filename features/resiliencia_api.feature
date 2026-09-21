Feature: API resilience and protocol boundary tests for Open-Meteo
  As a software integrator
  I want to verify how the API responds to anomalous requests, incomplete parameters and headers
  In order to validate robustness, controlled error messages and API behavior

  Scenario Outline: Validation against coordinates outside the allowed geographic range
    Given I configure an invalid coordinate with latitude <latitude> and longitude <longitude>
    When I query the weather forecast on Open-Meteo
    Then the response should have a 400 status code
    And the response should indicate a controlled error with a descriptive reason

    Examples:
      | latitude | longitude | reason                        |
      |    999.0 |  -82.5422 | Latitude greater than 90 degrees   |
      |    -95.0 |    -80.0  | Latitude lower than -90 degrees    |
      |   8.8080 |    250.0  | Longitude greater than 180 degrees |
      |   8.8080 |   -250.0  | Longitude lower than -180 degrees  |

  Scenario Outline: Validation against non-numeric data types
    Given I configure anomalous parameters with latitude "<latitude_str>" and longitude "<longitude_str>"
    When I query the weather forecast with text parameters
    Then the response should have a 400 status code
    And the response should indicate a controlled error with a descriptive reason

    Examples:
      | latitude_str | longitude_str | reason                    |
      | panama_city  | -79.5         | Text instead of latitude  |
      | 8.8080       | invalid       | Text instead of longitude |

  Scenario: Handling a request with a missing required parameter (latitude without longitude)
    Given I configure a request with only the latitude parameter "8.8080" and no longitude
    When I query the weather forecast with incomplete parameters
    Then the response should have a 400 status code
    And the response should indicate a controlled error with a descriptive reason

  Scenario: Evaluation of conditional headers (clarification for unsupported HTTP 412)
    Given I configure a valid request for Volcán Barú with conditional header "If-Match"
    When I query the weather forecast with conditional headers
    Then the response should have a 200 status code
    And it is confirmed that the public API does not implement HTTP 412 since it is a stateless read-only service
