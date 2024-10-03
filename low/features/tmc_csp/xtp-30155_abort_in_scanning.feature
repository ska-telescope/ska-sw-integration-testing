@XTP-30155 @XTP-29682 @tmc_csp
Scenario: Abort scanning CSP using TMC
    Given TMC and CSP subarray busy scanning
    When I command it to Abort
    Then the CSP subarray should go into an aborted obsState
    And the TMC subarray node obsState transitions to ABORTED
