Feature: This feature describes assigning, releasing, and configuring resources for the Low telescope with two subarrays, 
    including expected state transitions across TMC, CSP, SDP, and MCCS subsystems.

    @XTP-77663 @XTP-64112
    Scenario: Configure two Low telescope subarrays using TMC
        Given a Low telescope
        And telescope is in ON state
        And I assign station 1 to subarray 1
        And I assign station 2 to subarray 2
        When I configure the two subarrays for scan
        Then the TMC, CSP, SDP, and MCCS subarray instances 1 and 2 transition to CONFIGURING obsState
        And the TMC, CSP, SDP, and MCCS subarrays instances 1 and 2 transition to READY obsState


    
