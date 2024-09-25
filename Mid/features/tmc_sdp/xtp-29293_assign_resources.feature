# This BDD test performs TMC-SDP pairwise testing to verify AssignResources command flow.
@XTP-29293 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: Assign resources to SDP subarray using TMC
    Given the Telescope is in ON state
    And the subarray <subarray_id> obsState is EMPTY
    When I assign resources with the <receptors> to the subarray <subarray_id>
    Then the sdp subarray <subarray_id> obsState is IDLE
    And the TMC subarray <subarray_id> obsState is transitioned to IDLE
    And the correct resources <receptors> are assigned to sdp subarray and TMC subarray
    Examples:
        | subarray_id | receptors                                |
        | 1           | ('SKA001', 'SKA036', 'SKA063', 'SKA100') |
        