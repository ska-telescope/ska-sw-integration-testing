# This BDD test performs TMC-CSP pairwise testing to verify ReleaseResources command flow.
@XTP-29583 @XTP-29260 @tmc_csp
Scenario: Release resources from CSP subarray using TMC
    Given the telescope is in ON state
    And TMC subarray <subarray_id> is in IDLE ObsState
    When I release all resources assign to TMC subarray <subarray_id>
    Then the CSP subarray <subarray_id> must be in EMPTY ObsState
    And the TMC subarray <subarray_id> transitions to ObsState EMPTY
    Examples:
    | subarray_id |
    | 1           |
    