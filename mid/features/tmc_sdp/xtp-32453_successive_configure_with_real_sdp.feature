Feature:  TMC executes successive configure commands with real sdp devices
    @XTP-29381 @XTP-32453 @tmc_sdp @Team_SAHYADRI
    Scenario: TMC validates reconfigure functionality with real sdp devices
        Given a TMC and SDP
        And a subarray <subarray_id> in the IDLE obsState
        When the command configure is issued with <input_json1>
        And the subarray transitions to obsState READY
        And the next successive configure command is issued with <input_json2>
        Then the subarray <subarray_id> reconfigures changing its obsState to READY

        Examples:
            | subarray_id  | input_json1           |      input_json2       |
            | 1  | configure1_mid   |   configure2_mid  |
            | 1  | configure1_mid   |   configure1_mid  |
            



