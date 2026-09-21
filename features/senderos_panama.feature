Feature: Microclimate and elevation validation for Panama trails
  As a hiker
  I want to check the weather conditions and elevation of the trail I plan to visit
  In order to prepare for the weather and terrain conditions before starting the hike

  Scenario Outline: As a hiker I want to check the current weather conditions of the trail
    Given I choose the trail "<trail>" with coordinates latitude <latitude> and longitude <longitude>
    When I query the weather forecast on Open-Meteo
    Then the response should have a 200 status code
    And the response time should be less than 2.0 seconds
    And the data should include the current temperature and relative humidity

    Examples:
      | trail                                | latitude | longitude |
      | Volcán Barú (Chiriquí)               |  8.8080 | -82.5422 |
      | Cerro Trinidad (Capira)              |  8.7618 | -79.9961 |
      | La India Dormida (El Valle de Antón) |  8.6041 | -80.1432 |

  @verified
  Scenario Outline: As a hiker I want to verify the elevation of the confirmed trail
    Given I choose the trail "<trail>" with coordinates latitude <latitude> and longitude <longitude>
    When I query the Open-Meteo elevation service
    Then the response should have a 200 status code
    And the response time should be less than 2.0 seconds
    And the reported elevation should be within the range of <min_elevation> to <max_elevation> masl

    Examples:
      | trail                   | latitude | longitude | min_elevation | max_elevation |
      | Volcán Barú (Chiriquí)  |  8.8080 | -82.5422 |          3300 |          3550 |

  @possible_bug
  Scenario Outline: As a hiker I want to verify the elevation of trails under investigation
    # NOTE: Cerro Trinidad (max height ~950 masl) and La India Dormida (~800-900 masl) show a
    # discrepancy with the altitude returned by Open-Meteo (224 masl and 588 masl) for these
    # coordinates. Tagged with @possible_bug to cross-check against field surveys and
    # topographic models.
    Given I choose the trail "<trail>" with coordinates latitude <latitude> and longitude <longitude>
    When I query the Open-Meteo elevation service
    Then the response should have a 200 status code
    And the response time should be less than 2.0 seconds
    And the reported elevation should be within the range of <min_elevation> to <max_elevation> masl

    Examples:
      | trail                                 | latitude | longitude | min_elevation | max_elevation |
      | Cerro Trinidad (Capira)               |  8.7618 | -79.9961 |           750 |           950 |
      | La India Dormida (El Valle de Antón)  |  8.6041 | -80.1432 |           700 |           900 |
