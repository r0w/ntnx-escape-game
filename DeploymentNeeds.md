# Prerequisites
[x] HPOC with 4 nodes, and services activated :
  - Self service
  - Microseg
  - Leap
[x] Versions :
 - AOS : 7.3
 - PC : 7.3.1

Note : 
 - Policy engine and Intelligent Ops should be already activated/deployed
 - lab project is pre-created

# Manual Operations
Deploy Runbook `Prerequisites`
 - Upload it from github in `lab` project
 - Launch it

Deploy blueprint `DeployGame`
 - Upload it from github in `lab` project
 - Update credentials with `nutanix / nutanix/4u`
 - Select cluster and primary Network
 - Launch-it

[text](about:blank#blocked)
# Deployment of game through BP

## Runbook
[x] Create endopint `AD`

## Main BP
[x] Deploy new VM
[x] Install CalmDSL
[x] Create python venv in /home/nutanix/.calm/venv
[x] pip modules
[x] Remove 1 host
[-] Check new node is available with command 'api/clustermgmt/v4.0.b2/config/clusters/%s/rackable-units'
[x] Create 3 local users (Charlie, Thom and William)
[x] Create user thebadguy/MyProdPassword in the AD (IP .41)
[x] Project 'production' with cluster and thebadguy as admin
[x] Create VMs into this project
[x] Launch Inventory
[x] Create endpoint Jumphost in production poejct
[X] Deploy Clone BP
  [X] Upload
  [X] Change Credential
  [X] Update variables
[x] Create TestNetwork
[x] Deploy fakes BP
[x] Migrate subnets
[x] Clone git repo
[x] Create conf.env from template
[x] Add day2 actions
 - [] launch servers (DOES NOT WORK)
 - [x] reset game

# Notes :
 - [] Double-check node available in lab
 - [] Double-check project creation with user (in preparation - 2nd try seems ok)
 - [x] registry for calmdsl container
