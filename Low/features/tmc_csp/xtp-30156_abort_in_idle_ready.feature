@XTP-30156 @XTP-29682 @tmc_csp
Scenario: Abort resourced CSP and TMC subarray
    Given TMC subarray in obsState <obsstate>
    When I command it to Abort
    Then the CSP subarray should go into an aborted obsState
    And the TMC subarray node obsState transitions to ABORTED
    Examples:
        | obsstate |
        | IDLE     |
