@XTP-30167 @XTP-29682 @tmc_csp
Scenario: TMC executes a Restart on CSP subarray when subarray completes abort
    Given the telescope is in ON state
    And TMC and CSP subarray <subarray_id> is in obsState ABORTED
    When I command it to Restart
    Then the CSP subarray transitions to obsState EMPTY
    And the TMC subarray transitions to obsState EMPTY
    Examples:
        | subarray_id |
        | 1           |
