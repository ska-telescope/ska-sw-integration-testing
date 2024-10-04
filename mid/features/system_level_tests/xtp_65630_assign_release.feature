# This BDD test performs Assign and Release command flow on Mid integration
@XTP-65630 @XTP- @SAHYADRI
Scenario: Assign and Release resources to mid subarray
    Given the Telescope is in ON state
    And subarray <subarray_id> is in EMPTY ObsState
    When I assign resources to the subarray
    Then the CSP, SDP and TMC subarrays must be in IDLE obsState
    When I release all resources assigned to it
    Then the CSP, SDP and TMC subarray must be in EMPTY obsState
    Examples: 
        | subarray_id |
        | 1           |