# This BDD test performs TMC-CSP pairwise testing to verify Configure command flow.
@XTP-29583 @XTP-29345 @tmc_csp
Scenario Outline: Configure a CSP subarray for a scan using TMC
    Given the telescope is in ON state
    And TMC subarray <subarray_id> in ObsState IDLE
    When I issue the Configure command to the TMC subarray <subarray_id>
    Then the CSP subarray  <subarray_id> transitions to ObsState READY
    And the TMC subarray <subarray_id> transitions to ObsState READY
    And CSP subarray leaf node <subarray_id> starts generating delay values
    Examples:
    | subarray_id |
    | 1           |
    