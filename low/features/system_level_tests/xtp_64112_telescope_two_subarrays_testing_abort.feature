Feature: This feature describes Abort and Restart workflows for the Low telescope with two subarrays, 
    including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC for IDLE
        Given a Low telescope
        And telescope is in ON state
        And 2 subarrays are in obsState IDLE
        When I Abort subarray1
        Then subarray1 goes to obstate= empty
        And subarray2 continues to be in Obstate=ready with the originally assigned resources and configuration

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC for READY
        Given a Low telescope
        And telescope is in ON state
        And 2 subarrays are in obsState IDLE
        And a Telescope with 2 subarrays configured for a READY
        When I Abort subarray1
        Then subarray1 goes to obstate= empty 
        And subarray2 continues to be in Obstate=ready with the originally assigned resources and configuration

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC
        Given a Low telescope
        And telescope is in ON state
        And 2 subarrays are in obsState IDLE
        And a Telescope with 2 subarrays configured for a READY (i.e. ObsState=Ready)
        When I invoke scan command on two subarrays
        When I Abort subarray1
        Then subarray1 goes to obstate= empty 
        And subarray2 continues to be in Obstate=ready after the scan duration

    XTP-78765 @XTP-64112
    Scenario: Verify Abort-Restart workflow on Subarray 1 in obsState CONFIGURING while subarray 2 is configured successfully
        Given a Low telescope
        And telescope is in ON state
        And 2 subarrays are in obsState IDLE
        And 2 subarrays are in obsState CONFIGURING
        When I Abort subarray 1
        Then subarray 1 goes to obstate ABORTED
        And subarray 2 continues to be in Obstate=ready with the originally assigned resources and configuration

    XTP-78777 @XTP-64112
    Scenario: Verify Abort-Restart workflow on Subarray 1 in obsState resourcing while the resources are assigned to subarray 2 successfully
        Given a Low telescope
        And telescope is in ON state
        And 2 subarrays are in obsState RESOURCING
        When I Abort subarray 1
        Then subarray 1 goes to obstate ABORTED
        And subarray 2 is assigned with the resources successfully
