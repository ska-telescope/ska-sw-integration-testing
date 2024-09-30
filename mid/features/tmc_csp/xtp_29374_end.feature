# This BDD test performs TMC-CSP pairwise testing to verify End command flow.
@XTP-29583 @XTP-29374 @tmc_csp
Scenario: End configure from CSP Subarray using TMC
    Given the telescope is in ON state
    And TMC subarray <subarray_id> is in READY ObsState
    When I issue End command to TMC subarray <subarray_id>
    Then the CSP subarray transitions to ObsState IDLE
    And the TMC subarray <subarray_id> transitions to ObsState IDLE
    Examples:
    | subarray_id |
    | 1           |
    