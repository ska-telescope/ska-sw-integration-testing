@XTP-29855 @XTP-29682 @tmc_csp
Scenario: End Command to CSP subarray using TMC
    Given the Telescope is in ON state
    And a subarray <subarray_id> in the READY obsState
    When I issue End command to the subarray
    Then the CSP subarray transitions to IDLE obsState
    And TMC subarray transitions to IDLE obsState
    Examples:
        | subarray_id   |
        |  1            |