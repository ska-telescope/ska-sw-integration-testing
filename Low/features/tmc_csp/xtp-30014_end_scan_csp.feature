@XTP-30014 @XTP-29682 @tmc_csp
Scenario: TMC executes a EndScan command on CSP subarray
    Given the Telescope is in ON state
    And TMC subarray <subarray_id> is in SCANNING obsState
    When I issue the Endscan command to the TMC subarray
    Then the CSP subarray transitions to obsState READY
    And the TMC subarray transitions to obsState READY
    Examples:
        | subarray_id |
        | 1           |