Feature: Mid Telescope State Transitions

  This feature covers the transition of a mid telescope through various states such as ON, OFF, and STANDBY, 
  including the state changes in the SDP, CSP, and DishMaster subsystems.

  @XTP-66801 @XTP-65506 @TEAM_SAHYADRI
  Scenario: Starting up mid telescope
      Given a mid telescope
      And a Telescope consisting of SDP, CSP and DISH that is OFF
      When I invoke the ON command on the telescope
      Then the Telescope consisting of SDP and CSP devices should transition to ON state
      And DishMaster must transition to STANDBY-FP mode

  @XTP-66801 @XTP-67219 @TEAM_SAHYADRI
  Scenario: Switch off the mid telescope
      Given a mid telescope
      And a Telescope consisting of SDP, CSP and DISH that is ON
      When I invoke the OFF command on the telescope
      Then the Telescope consisting of SDP and CSP devices should transition to OFF state
      And DishMaster must transition to STANDBY-LP mode

  @XTP-66801 @XTP-66810 @TEAM_SAHYADRI
  Scenario: Standby the mid telescope
      Given a mid telescope
      And a Telescope consisting of SDP, CSP and DISH that is ON
      When I invoke the STANDBY command on the telescope
      Then the Telescope consisting of SDP and CSP devices should transition to STANDBY state