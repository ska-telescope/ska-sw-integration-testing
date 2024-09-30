Feature: TMC executes successive assign commands with real sdp devices
        @XTP-29381  @XTP-32452 @tmc_sdp @Team_SAHYADRI
        Scenario Outline: Validate second AssignResources command  after first successful AssignResources and ReleaseResources are executed
            Given the TMC and SDP subarray <subarray_id> in the IDLE obsState
            When I release all resources assigned to TMC subarray <subarray_id>
            Then TMC and SDP subarray <subarray_id> must be in EMPTY obsState
            And AssignResources is executed with updated <input_json1> on TMC subarray <subarray_id>
            And TMC and SDP subarray <subarray_id> transitions to IDLE obsState
            Examples:
            | subarray_id  | input_json1   |                                                 |
            | 1            | assign_resources_mid |
            
