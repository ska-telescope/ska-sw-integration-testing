# This BDD test performs Assign and Release command flow on Mid integration
@XTP-65630 @XTP-66801 @SAHYADRI
Scenario: Assign and Release resources to Mid subarray
    Given the Telescope is in ON state
    And subarray is in EMPTY ObsState
    When I assign resources to the subarray
    Then the TMC, CSP and SDP subarrays transition to RESOURCING obsState
    And the CSP, SDP and TMC subarrays must be in IDLE obsState
    When I release all resources assigned to it
    Then the CSP, SDP and TMC subarrays must be in EMPTY obsState