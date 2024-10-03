# This BDD test performs AssignResources command flow on Mid integration

Scenario: Assign resources to mid subarray
    the Telescope is in ON state
    And subarray <subarray_id> is in EMPTY ObsState
    When I assign resources to the subarray
    Then the CSP, SDP and TMC subarrays must be in IDLE obsState
    Examples: 
        | subarray_id |
        | 1           |

Scenario: Release resources from mid Subarray
    Given the Telescope is in ON state
    And subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to it
    Then the CSP, SDP and TMC subarray must be in EMPTY obsState
    And subarray obsState is transitioned to EMPTY
    Examples:
        | subarray_id   |   
        |  1            |
