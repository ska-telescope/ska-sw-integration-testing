Scenario: Assign resources to low subarray
    Given a low telescope
    And telescope is in ON state
    And subarray <subarray_id> is in EMPTY ObsState
    When I assign resources to the subarray
    Then the CSP, SDP and MCCS subarrays must be in IDLE obsState
    And the subarray obsState is transitioned to IDLE        
    Examples: 
        | subarray_id |
        | 1           |


Scenario: Release resources from low Subarray
    Given a low telescope
    Given telescope is in ON state
    And subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to it
    Then the CSP, SDP and MCCS subarray must be in EMPTY obsState
    And subarray obsState is transitioned to EMPTY
    Examples:
        | subarray_id   |   
        |  1            |