# Content

## Setup 

- [x] Create an alternative admin user
- [x] Connect with it
- [x] Create a project
- [x] Create a subnet
- [x] Add an image
- [x] Create a new VM with user
- [x] Check with prod user it is not viewable
- [x] Move the VM on another node
- [x] Create a category
- [x] Securize the VM
	- [x] Encryption
	- [x] Microseg
	- [x] Snap
- [x] Create approval rule to prevent deletion of RP
- [x] VM has been deleted, restore VM from recovery point

## Operational help

- [x] Create report to send-it regularly to an email
- [x] Add a node OK (just view)
- [x] LCM (just view)
- [x] Security dashboard (just view)
- [x] Cluster Runaway (on Specialists HPOC ?)
	- Identify bad sized VM (on Specialists HPOC ?) with `Optimize resources`
- [x] Create Playbook to call a webhook as soon as VM is restarted
- [x] Clone prod into a VPC
	- [x] do it once
	- [x] Schedule a refresh 
- [x] Change app in marketplace to add (spying) task

# Game Improvement
 - [x] Use Web interface to connect on game
 - [x] Script/BP to setup everything on a HPOC
 - [x] recovery mode
 - [x] Script/BP to send starting email
 - [] Summary webpage/email to summarize the lab and Nutanix platform features
 - [] Medals system (if some stages are done in limited time)
 - [] Update prerequisites runbook to deploy main bp and launch-it during preparation task ?
 - [] Support multiple games

# Additional content for next release
- Create file share
- Create DB
- Create bucket

- If you need to setup a stage to a user, you can look at [gameContent.json](gameContent.json) file to identify the stage number you need to use. You can then use a Day 2 Operations actions to make the user go to the desired stage using his 3-letters pseudo.