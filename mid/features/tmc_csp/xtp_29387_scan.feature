# This BDD test performs TMC-CSP pairwise testing to verify Scan command flow.
@XTP-29583 @XTP-29387 @tmc_csp
Scenario: TMC executes a Scan command on CSP subarray.
    Given the telescope is in ON state
    And TMC subarray <subarray_id> is in READY ObsState
    When I issue the scan command to the TMC subarray <subarray_id>
    Then the CSP subarray transitions to ObsState SCANNING
    And the TMC subarray <subarray_id> transitions to ObsState SCANNING
    And the CSP subarray ObsState transitions to READY after the scan duration elapsed
    And the TMC subarray <subarray_id> ObsState transitions back to READY
    Examples:
        | subarray_id |
        | 1 |
        