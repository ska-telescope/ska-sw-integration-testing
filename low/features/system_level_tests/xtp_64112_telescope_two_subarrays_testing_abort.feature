Feature: This feature describes Abort and Restart workflows for the Low telescope with two subarrays, 
    including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC for IDLE
        Given a Low telescope
        And telescope is in ON state
        And a Telescope with 2 subarrays configured for a IDLE
        When I Abort subarray1
        then subarray1 goes to obstate= empty 
        And subarray2 continues to be in Obstate=ready with the originally assigned resources and configuration

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC for READY
        Given a Low telescope
        And telescope is in ON state
        And a Telescope with 2 subarrays configured for a IDLE
        And a Telescope with 2 subarrays configured for a READY
        When I Abort subarray1
        then subarray1 goes to obstate= empty 
        And subarray2 continues to be in Obstate=ready with the originally assigned resources and configuration

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC
        Given a Low telescope
        And telescope is in ON state
        And a Telescope with 2 subarrays configured for a IDLE
        And a Telescope with 2 subarrays configured for a READY (i.e. ObsState=Ready)
        When I invoke scan command on two subarrays
        When I Abort subarray1
        then subarray1 goes to obstate= empty 
        And subarray2 continues to be in Obstate=ready with the originally assigned resources and configuration