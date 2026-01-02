# ntnx-escape-game
  - Roleplay to discover the **Nutanix Cloud Platform** (NCP).

# Preparation
1) Book a Nutanix HPoC with the following characteristics: 
  - 4 nodes cluster (no more, no less) cause one node will be removed by the scripts.
  - AOS 7.5 (do not use another version).
  - PC 7.5 (do not use another version).
  - Self-Service enabled and version 4.3 (do not use another version).
  - Leap Enabled.
  - Flow security enabled.

2) In PC > Self-service, upload the **runbook** `materials/EG-Runbook-Prerequisites.json` in the `lab` project.
  - **!!! WARNING !!!** 
    - Ensure you are in the **Runbooks** section (and not in Blueprints) or upload will fail.
  - Launch the runbook.

3) Upload the **blueprint** `materials/EG-Blueprint-Installation.json` in the `lab` project.
  - **!!! WARNING !!!**
    - Ensure you have launched the runbook first or you'll have problems.
    - 1st task of the blueprint checks AD credential. If tasks fails, please delete the app, change AD Endpoint credentials, and then redeploy the app from the BP.
  - Update credentials using the button in the blueprint:
    - Update NUTANIX credential with password `nutanix/4u`
    - Update PLAYER credential with password `keepgoing`
  - Save the blueprint.
  - Launch it.
  - Chose a name of your choice for the application that will be deployed.
  - Fill the form with required values:
    - Ask to the Escape Game Team the values that you need.
    - In the `Game` section at the end of the form, select your Cluster and its Primary Network.
    - Click on `deploy`.

# Known Issues: 
  - **!!! IMPORTANT !!!**
  - 1st time importing the installation blueprint (step 3) may fail on a newly deployed HPoC. Retry and 2nd upload should works.
  - Please confirm the cluster has only 3 nodes at the end of the installation (experienced an issue once, because of erasure-coding). If not, please remove 4th node manually.

# Player prerequisites
  - Internet Access.
  - If you want to use VPN access, ensure your players have installed and tested it first.

# Game and Dashboard
  - Look at the description of the application deployed by the blueprint, you'll find:
    - The URL to access the ChatBot and play and it will be mentioned in the invitation email too.
    - The URL of the scoreboard, that is a sort of dashboard monitoring the progress of all the players. We recommand to display the scoreboard on a screen, cause it will improve game feeling for players.

  - Use Day 2 actions of the blueprint to:
    - Launch invitation email to your players, but you'll have to enter recipients list.
    - Launch "End of lab" email. Then used recipients list to send invites will be used.
    - **Note:** Day-2 operations can be found clicking on `Self-Service > Application > {your application} > Manage tab`. You can run them by clicking on play icon, just after the day-2 action name.

# Tips
  - Unsuccesfull lab checks may happen even if the exercise is succesfully done. In this case, the player can refresh is web page, use the same trigram, and recovery mode will bring him to the same lab step, that could then be checked again and passed successfully.

  - This is caused by ID memorized by script during execution, but not existing anymore (for exemple, if the player has deleted and recreated OS image, the game will wait the old ID, not the new one).
  

