Feature: Commands with invalid json input
    Scenario: AssignResource command with invalid JSON is rejected by the TMC
        Given the TMC is in ON state
        And the subarray is in EMPTY obsState
        When the command AssignResources is invoked with <invalid_json> input
        Then TMC should reject the AssignResources command
        And TMC subarray remains in EMPTY obsState
        And TMC successfully executes AssignResources for subarray with a valid input json
        Examples:
            | invalid_json                  |
            | missing_pb_id_key             |
            | missing_scan_type_id_key      |
            | missing_count_key             |
            | missing_receptor_id_key       |

    @XTP-41255
    Scenario:   Invalid json rejected by TMC Low for Configure command
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command Configure is invoked with <invalid_json> input
        Then the TMC should reject the <invalid_json> with ResultCode.Rejected
        And TMC subarray remains in IDLE obsState
        And TMC successfully executes the Configure command for the subarray with a valid json

        Examples:
            | invalid_json                   |
            | csp_key_missing                |
            | sdp_key_missing                |
            | mccs_key_missing               |
            | scan_duration_key_missing      |
            | empty_string                   |
            