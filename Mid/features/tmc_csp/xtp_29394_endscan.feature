# This BDD test performs TMC-CSP pairwise testing to verify EndSCan command flow.
@XTP-29583 @XTP-29394 @tmc_csp
Scenario: TMC executes a EndScan command on CSP subarray.
    Given the telescope is in ON state
    And TMC subarray <subarray_id> is in Scanning ObsState
    When I issue the Endscan command to the TMC subarray <subarray_id>
    Then the CSP subarray transitions to ObsState READY
    And the TMC subarray <subarray_id> transitions to ObsState READY
    Examples:
        | subarray_id |
        | 1 |
        