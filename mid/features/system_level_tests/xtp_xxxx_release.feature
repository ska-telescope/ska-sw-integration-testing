# This BDD test performs ReleaseResources command flow on Mid integration repository

Scenario: Release resources using TMC
    Given TMC subarray <subarray_id> is in IDLE ObsState
    When I release all resources assign to TMC subarray <subarray_id>
    Then the CSP,SDP and TMC subarray <subarray_id> must be in EMPTY ObsState
    Examples:
    | subarray_id |
    | 1           |
