#!/bin/bash 

cd ~/.calm
source venv/bin/activate

pc_ip = "@@{PC_IP}@@"
pc_user = "@@{PC_USERNAME}@@"
pc_password = "@@{PC_PASSWORD}@@"

primary_subnet_name = "@@{PRIMARY_SUBNET}@@"
secondary_subnet_name = "@@{SECONDARY_SUBNET}@@"

python ~/ntnx-escape-game/scripts/create-project.py --pcIp $pc_ip --pcUser $pc_user --pcPassword $pc_password --primarySubnet $primary_subnet_name --secondarySubnet $secondary_subnet_name