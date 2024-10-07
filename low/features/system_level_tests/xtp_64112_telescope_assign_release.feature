@XTP-65635 @XTP-64112 @TEAM_HIMALAYA
Scenario: Assign resources to low subarray
    Given a Low telescope
    And telescope is in ON state
    And subarray is in EMPTY ObsState
    When I assign resources to the subarray
    Then TMC, CSP, SDP, and MCCS subarrays transition to RESOURCING obsState
    And the TMC, CSP, SDP, and MCCS subarrays transition to IDLE obsState

@XTP-65636 @XTP-64112 @TEAM_HIMALAYA
Scenario: Release resources from low subarray
    Given a Low telescope
    And telescope is in ON state
    And subarray is in the IDLE obsState
    When I release all resources assigned to it
    Then the TMC, CSP, SDP, and MCCS subarrays transition to EMPTY obsState