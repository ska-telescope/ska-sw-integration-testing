# This BDD test performs TMC-CSP pairwise testing to verify AssignResources-ReleaseResources-AssignResources command flow.
@XTP-40070 @XTP-29259 @tmc_csp
Scenario: Validate second AssignResources command after first successful AssignResources and ReleaseResources are executed
    Given the TMC and CSP subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to TMC subarray <subarray_id>
    Then TMC and CSP subarray <subarray_id> must be in EMPTY obsState
    When I invoked second AssignResources on TMC subarray <subarray_id>
    Then TMC and CSP subarray <subarray_id> transitions to IDLE obsState
    Examples:
        | subarray_id  |
        | 1            |

# This BDD test performs TMC-CSP pairwise testing to verify Succesive AssignResources command flow.
@XTP-40072 @XTP-29259 @tmc_csp
Scenario: Validate succesive AssignResources command
    Given TMC subarray <subarray_id> is in EMPTY ObsState
    When I invoke First AssignResources on TMC subarray <subarray_id> with <receptors1> on TMC subarray <subarray_id>
    Then CSP subarray <subarray_id> must be in IDLE ObsState
    And TMC subarray <subarray_id> must be in IDLE obsState
    And Resources are assigned to TMC subarray <subarray_id>
    When I invoke Second AssignResources on TMC subarray <subarray_id> with <receptors2> on TMC subarray <subarray_id>
    Then CSP subarray <subarray_id> must be in IDLE ObsState
    And TMC subarray <subarray_id> must be in IDLE obsState
    And Resources are assigned to TMC subarray <subarray_id>
    Examples:
    | subarray_id | receptors1          | receptors2          |
    | 1           | ["SKA001","SKA036"] | ["SKA063","SKA100"] |