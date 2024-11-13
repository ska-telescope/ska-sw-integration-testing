# SKA Software Integration Testing
 
This project focuses on the integration and release of all the subsystems for SKA telescopes, incorporating Telescope Low and Telescope Mid.

## Cloning the repository
Checkout the repository and ensure that submodules (including `.make`) are cloned with:
```
$ git clone https://gitlab.com/ska-telescope/ska-sw-integration-testing.git
$ cd ska-sw-integration-testing
```

## Deployments
### MID
#### Deployment for Mid telescope(system level integration testing)

Access Mid deployment pipelines via the following link https://gitlab.com/ska-telescope/ska-mid-integration

Click Run pipeline, default is to run against main

From pipeline stages, run the deploy-mid-integration job in integration stage


#### Deployment for Mid telescope(pairwise testing)

Access Mid deployment pipelines via the following link https://gitlab.com/ska-telescope/ska-mid-integration

Click Run pipeline, default is to run against main

From pipeline stages, run the deploy-tmc-with-csp, deploy-tmc-with-sdp, deploy-tmc-with-dish jobs in integration stage 

### Low

#### Deployment for Mid telescope(system level integration testing)

Access Mid deployment pipelines via the following link https://gitlab.com/ska-telescope/ska-low-integration

Click Run pipeline, default is to run against main

From pipeline stages, run the deploy-low-integration job in integration stage

#### Deployment for Mid telescope(pairwise testing)

Access Mid deployment pipelines via the following link https://gitlab.com/ska-telescope/ska-low-integration

Click Run pipeline, default is to run against main

From pipeline stages, run the deploy-tmc-with-csp, deploy-tmc-with-sdp, deploy-tmc-with-mccs jobs in integration stage 

## Steps to perform testing

### MID

For system level integration testing the defaul namespace will be `integration-ska-mid`

Before running the test testing pipeline make sure the deployment is successful 

Once the deployment is up and running , run the testing pipeline 

### LOW

For system level integration testing the defaul namespace will be `integration-ska-low`

Before running the test testing pipeline make sure the deployment is successful 

Once the deployment is up and running , run the testing pipeline