Feature:  Invalid unexpected commands
    Scenario: Unexpected commands not allowed when TMC subarray is empty
        Given the TMC is in ON state 
        And the subarray is in EMPTY obsstate
        When the command <unexpected_command> is invoked on that subarray
        Then TMC should reject the <unexpected_command> with ResultCode.Rejected
        And TMC subarray remains in EMPTY obsstate
        And TMC executes the AssignResources command successfully
        Examples:
            | unexpected_command   |
            | Configure            |
            | Scan                 |
            | End                  |
            | Abort                |

    Scenario: Unexpected commands not allowed when TMC subarray is idle
        Given the TMC is in ON state 
        And the subarray is in IDLE
        When the command <unexpected_command> is invoked on that subarray
        Then TMC should reject the <unexpected_command> with ResultCode.Rejected
        And TMC subarray remains in IDLE obsState
        And TMC executes the <permitted_command> command successfully
        Examples:
            | unexpected_command  | permitted_command  |
            | Scan                |   Configure        |   
            | Scan                |   ReleaseResources |

    Scenario: Unexpected commands not allowed when TMC subarray is in Assigning
        Given TMC is in ON state
        And the subarray is busy in assigning the resources
        When the command <unexpected_command> is invoked on the subarray
        Then TMC should reject the <unexpected_command> with ResultCode.Rejected
        And TMC executes the Configure command successfully
        Examples:
            | unexpected_command  | 
            | AssignResources     |    


    Scenario: Unexpected commands not allowed when TMC subarray is READY
        Given the TMC is in ON state 
        And the subarray is in READY obsState
        When the command <unexpected_command> is invoked on that subarray
        Then TMC should reject the <unexpected_command> with ResultCode.Rejected
        And TMC subarray remains in READY obsState
        And TMC executes the <permitted_command> command successfully
        Examples:
            | unexpected_command   | permitted_command |
            | AssignResources      | Configure         |
            | ReleaseResources     | Scan              |
            | EndScan              | End               |
            | EndScan              | Abort             |                  