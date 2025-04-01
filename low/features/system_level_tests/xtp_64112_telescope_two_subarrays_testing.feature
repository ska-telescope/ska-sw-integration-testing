Feature: This feature describes assigning, releasing, and configuring resources for the Low telescope with two subarrays, 
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


    
