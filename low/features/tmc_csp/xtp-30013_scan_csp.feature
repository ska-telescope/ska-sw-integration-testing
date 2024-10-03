@XTP-30013 @XTP-29682 @tmc_csp
Scenario: TMC executes a scan on CSP subarray
    Given the Telescope is in ON state
    Given TMC subarray <subarray_id> is in READY ObsState
    When I issue scan command on subarray
    Then the subarray obsState transitions to SCANNING
    And the CSP subarray obsState transitions to READY after the scan duration elapsed
    And the TMC subarray obsState transitions back to READY
    Examples:
        | subarray_id   | 
        |    1          |