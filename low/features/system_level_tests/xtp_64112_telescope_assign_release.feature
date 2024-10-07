@XTP-65635 @XTP-64112 @TEAM_HIMALAYA
Scenario Outline: Assign resources to low subarray
    Given a Low telescope
    And telescope is in ON state
    And subarray is in EMPTY ObsState
    When I assign resources to the subarray
    Then the TMC, CSP, SDP and MCCS subarrays transition to <obs_state> obsState     
    Examples: 
        | obs_state            |
        | RESOURCING           |
        | IDLE                 |

@XTP-65636 @XTP-64112 @TEAM_HIMALAYA
Scenario Outline: Release resources from low Subarray
    Given a Low telescope
    Given telescope is in ON state
    And subarray is in the IDLE obsState
    When I release all resources assigned to it
    Then the TMC, CSP, SDP and MCCS subarrays transition to EMPTY obsState
    Examples:
        | subarray_id   |   
        |  1            |