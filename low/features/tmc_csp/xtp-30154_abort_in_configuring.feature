@XTP-30154 @XTP-29682 @tmc_csp
Scenario: Abort configuring CSP using TMC
    Given TMC and CSP subarray busy configuring
    When I command it to Abort
    Then the CSP subarray should go into an aborted obsState
    And the TMC subarray node obsState transitions to ABORTED
