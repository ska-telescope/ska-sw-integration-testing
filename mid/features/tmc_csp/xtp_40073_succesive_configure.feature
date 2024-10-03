# This BDD test performs TMC-CSP pairwise testing to verify Succesive AssignResources command flow.
@XTP-40073 @XTP-29259 @tmc_csp
Scenario: TMC-CSP succesive configure functionality
    Given a TMC and CSP
    And a subarray <subarray_id> in the IDLE obsState
    When I invoke First Configure command on TMC subarray <subarray_id> with <input_json1>
    Then CSP subarray <subarray_id> must be in READY ObsState
    And TMC subarray <subarray_id> must be in READY obsState
    When I invoke Second Configure command on TMC subarray <subarray_id> with <input_json2>
    Then CSP subarray <subarray_id> must be in READY ObsState
    And TMC subarray <subarray_id> must be in READY obsState

    Examples:
        | subarray_id  | input_json1          |   input_json2      |
        | 1            | configure1_mid       |   configure1_mid   |
        | 1            | configure1_mid       |   configure2_mid   |