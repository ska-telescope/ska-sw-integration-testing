Feature: This feature describes assigning, releasing, configuring resources and Scan workflows for the Low telescope with two subarrays, 
    including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

    @XTP-77663 @XTP-64112
    Scenario: Execute Scans on two Low telescope subarrays using TMC
        Given a Low telescope
        And telescope is in ON state
        And I assign station 1 to subarray 1 and station 2 to subarray 2
        And I configure the two subarrays for scan
        When I invoke scan command on two subarrays
        Then the TMC, CSP, SDP and MCCS subarrays transition to SCANNING obsState
        And after the scan duration they transition back to READY obsState

    @XTP-64112
    Scenario: Execute Abort on two Low telescope subarrays using TMC
        Given a Low telescope
        And telescope is in ON state
        Given a Telescope with 2 subarrays configured for a IDLE
        Given a Telescope with subarray2 configured for a scan (i.e. ObsState=Ready)
        When I Abort subarray1 and restart it
        then subarray1 goes to obstate= empty 
        And subarray2 continues to be in Obstate=ready with the originally assigned resources and configuration