@XTP-32140
Scenario: TMC generates delay values
    Given the telescope is in ON state
    And subarray is in obsState IDLE
    When I configure the subarray
    Then CSP Subarray Leaf Node starts generating delay values
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values
