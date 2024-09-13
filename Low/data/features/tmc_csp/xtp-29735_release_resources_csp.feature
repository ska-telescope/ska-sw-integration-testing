@XTP-29735 @XTP-29682 @tmc_csp
Scenario: Release resources from CSP Subarray using TMC
    Given the Telescope is in ON state
    And TMC subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to it
    Then the CSP subarray must be in EMPTY obsState
    And TMC subarray obsState transitions to EMPTY
    Examples:
        | subarray_id   |   
        |  1            |