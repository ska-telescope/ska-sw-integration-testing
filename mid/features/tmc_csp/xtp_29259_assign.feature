# This BDD test performs TMC-CSP pairwise testing to verify AssignResources command flow.
@XTP-29583 @XTP-29259 @tmc_csp
Scenario: Assign resources to CSP subarray using TMC
    Given the telescope is in ON state
    And TMC subarray <subarray_id> is in EMPTY ObsState
    When I assign resources with <receptors> to TMC subarray <subarray_id>
    Then CSP subarray <subarray_id> transitioned to ObsState IDLE
    And TMC subarray <subarray_id> transitioned to ObsState IDLE
    And correct resources <receptors> are assigned to TMC subarray <subarray_id>
    Examples:
    | subarray_id | receptors                               |
    | 1           | 'SKA001', 'SKA036', 'SKA063', 'SKA100'  |
    