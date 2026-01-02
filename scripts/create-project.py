from jsonpath_ng.ext import parse
import requests
import time
import urllib3
import uuid
import json

urllib3.disable_warnings()

pc_ip="@@{PC_IP}@@"
pc_user="@@{PC_USERNAME}@@"
pc_pwd='@@{PC_PASSWORD}@@'

primary_subnet_name="@@{PRIMARY_SUBNET}@@"
secondary_subnet_name="@@{SECONDARY_SUBNET}@@"

projectName="production"
projectAdmin="thebadguy"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Check if project already exists
projects_list_url = "https://%s:9440/api/nutanix/v3/projects/list" % pc_ip
payload_list = {"kind":"project","filter": f"name=={projectName}"}
r = requests.post(projects_list_url, json=payload_list, headers=headers, verify=False, auth=(pc_user, pc_pwd))
rd = r.json()
if rd.get('entities'):
    print(f"Project '{projectName}' already exists! Assuming this script has already been executed.")
    print(f"Exiting...")
    exit(0)

# Get Account
url="https://%s:9440/api/nutanix/v3/accounts/list" % pc_ip

payload = {
    "kind": "account"
    }

response = requests.post(url, json=payload, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

jsonpath_expr = parse('$.entities[?(@.metadata.name=="NTNX_LOCAL_AZ")].metadata.uuid')

for match in jsonpath_expr.find(response_data):
    account_uuid = match.value

# Get Subnets
url="https://%s:9440/api/networking/v4.0/config/subnets" % pc_ip

payload = {
    "kind": "subnet"
    }

response = requests.get(url, json=payload, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

jsonpath_expr = parse('$.data[?(@.name=="' + primary_subnet_name + '")].extId')

for match in jsonpath_expr.find(response_data):
    primary_subnet_uuid = match.value

jsonpath_expr = parse('$.data[?(@.name=="' + secondary_subnet_name + '")].extId')

for match in jsonpath_expr.find(response_data):
    secondary_subnet_uuid = match.value  

# Get Clusters
url="https://%s:9440/api/nutanix/v3/clusters/list" % pc_ip

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

payload = {
    "kind": "cluster"
    }

response = requests.post(url, json=payload, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

jsonpath_expr = parse('$.entities[?(@.spec.name!="Unnamed")].metadata.uuid')

for match in jsonpath_expr.find(response_data):
    cluster_uuid = match.value

# Create Project
url="https://%s:9440/api/nutanix/v3/projects" % pc_ip

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

payload =  {
    "metadata": {
        "kind": "project",
    },
    "spec": {
        "name": projectName,
        "description": "Production Project",
        "resources": {
            "resource_domain": {
                "resources": []
            },
            "account_reference_list": [
                {
                    "kind": "account",
                    "uuid": account_uuid
                }
            ],
            "cluster_reference_list": [
                {
                    "kind": "cluster",
                    "uuid": cluster_uuid
                }
            ],
            "default_subnet_reference": {
                "kind": "subnet",
                "uuid": primary_subnet_uuid
            },            
            "subnet_reference_list": [
                {
                    "kind": "subnet",
                    "name": "primary",
                    "uuid": primary_subnet_uuid
                },
                {
                    "kind": "subnet",
                    "name": "secondary",
                    "uuid": secondary_subnet_uuid
                }
            ],

        }
    }
}

response = requests.post(url, json=payload, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()
taskID = response_data['status']['execution_context']['task_uuid']

print("We check Task UUID: " + taskID)

ended=False
url="https://%s:9440/api/nutanix/v3/tasks/%s" % (pc_ip,taskID)

while not ended:
    response = requests.get(url, headers=headers, verify=False, auth=(pc_user, pc_pwd))
    response_data = response.json()
    if response_data['status']=="SUCCEEDED":
        projectUUID=response_data['entity_reference_list'][0]['uuid']
        break;
    elif response_data['status']=="FAILED":
        exit(1)
    else:
        time.sleep(5)


# Get Spec version
url="https://%s:9440/api/nutanix/v3/projects/%s" % (pc_ip,projectUUID)
response=requests.get(url, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

projectSpecVersion=response_data['metadata']['spec_version']

print("Project UUID: " + projectUUID + " / Version: " + str(projectSpecVersion))

## Add User

# Get AD Service
url = "https://%s:9440/api/iam/v4.0/authn/directory-services" % pc_ip

response = requests.get(url, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

directoryType = response_data['data'][0]['directoryType']
directoryID=response_data['data'][0]['extId']

# Add TheBadGuy into the users
url = "https://%s:9440/api/iam/v4.0/authn/users" % pc_ip

payload = {
    "firstName": "Henry",
    'lastName': "Ugly",
    "displayName": projectAdmin,
    "username": projectAdmin,
    "userType": "LDAP",
    "idpId": directoryID,
}

response = requests.post(url, json=payload, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

# Get UserID
url="https://%s:9440/api/iam/v4.0/authn/users" % pc_ip

response = requests.get(url, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()

jsonpath_expr = parse("$.data[?(@.username=='" + projectAdmin + "')].extId")

for match in jsonpath_expr.find(response_data):
    userUUID = match.value

print("User UUID: " + userUUID)

# We get Project Admin role UUID
url = "https://%s:9440/api/iam/v4.0/authz/roles" % pc_ip

response = requests.get(url, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data = response.json()
#print(json.dumps(response_data, indent=4))

jsonpath_expr = parse("$.data[?(@.displayName=='Project Admin')].extId")

for match in jsonpath_expr.find(response_data):
    projectAdminRoleUUID = match.value

print("Role 'Project Admin' UUID: " + projectAdminRoleUUID)

# Update project to add user

payload = {
    "api_version": "3.1",
    "metadata": {
        "project_reference": {
            "kind": "project",
            "name": projectName,
            "uuid": projectUUID
        },
        "spec_version": projectSpecVersion,
        "kind": "project",
        "uuid": projectUUID,
    },
    "spec": {
        "project_detail": {
            "name": "production",
            "resources": {
                "account_reference_list": [
                    {
                        "kind": "account",
                        "uuid": account_uuid
                    }
                ],
                "user_reference_list": [
                    {
                        "name": projectAdmin,
                        "kind": "user",
                        "uuid": userUUID
                    }
                ],
                "default_subnet_reference": {
                    "kind": "subnet",
                    "uuid": primary_subnet_uuid
                },
                "subnet_reference_list": [
                    {
                        "kind": "subnet",
                        "name": "secondary",
                        "uuid": secondary_subnet_uuid
                    },
                    {
                        "kind": "subnet",
                        "name": "primary",
                        "uuid": primary_subnet_uuid
                    }
                ],
                "cluster_reference_list": [
                    {
                        "kind": "cluster",
                        "uuid": cluster_uuid
                    }
                ],
                "enable_directory_and_identity_provider_shortlist": False,
            },
            "description": "Production Project"
        },
        "user_list": [
            {
                "metadata": {
                    "kind": "user",
                    "uuid": userUUID
                },
                "user": {
                    "resources": {
                        "directory_service_user": {
                            "user_principal_name": projectAdmin,
                            "directory_service_reference": {
                                "uuid": directoryID,
                                "kind": "directory_service"
                            }
                        }
                    }
                },
                "operation": "ADD"
            }
        ],
        "access_control_policy_list": [
            {
                "acp": {
                    "name": "nuCalmAcp-"+str(uuid.uuid4()),
                    "resources": {
                        "role_reference": {
                            "name": "Project Admin",
                            "uuid": projectAdminRoleUUID,
                            "kind": "role"
                        },
                        "user_reference_list": [
                            {
                                "name": projectAdmin,
                                "kind": "user",
                                "uuid": userUUID
                            }
                        ],
                        "filter_list": {
                            "context_list": [
                                {
                                    "scope_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": "PROJECT",
                                            "right_hand_side": {
                                                "uuid_list": [
                                                    projectUUID
                                                ]
                                            }
                                        }
                                    ],
                                    "entity_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "ALL"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "entity_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "image"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "marketplace_item"
                                            },
                                            "right_hand_side": {
                                                "collection": "SELF_OWNED"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "directory_service"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            },
                                            "left_hand_side": {
                                                "entity_type": "role"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "right_hand_side": {
                                                "uuid_list": [
                                                    projectUUID
                                                ]
                                            },
                                            "left_hand_side": {
                                                "entity_type": "project"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "environment"
                                            },
                                            "right_hand_side": {
                                                "collection": "SELF_OWNED"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            },
                                            "left_hand_side": {
                                                "entity_type": "app_icon"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            },
                                            "left_hand_side": {
                                                "entity_type": "category"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "app_task"
                                            },
                                            "right_hand_side": {
                                                "collection": "SELF_OWNED"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "app_variable"
                                            },
                                            "right_hand_side": {
                                                "collection": "SELF_OWNED"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "identity_provider"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "vm_recovery_point"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "report_config"
                                            },
                                            "right_hand_side": {
                                                "collection": "SELF_OWNED"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "virtual_network"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "resource_type"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "custom_provider"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "distributed_virtual_switch"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "container"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "cluster"
                                            },
                                            "right_hand_side": {
                                                "uuid_list": [
                                                    cluster_uuid
                                                ]
                                            }
                                        }
                                    ]
                                },
                                {
                                    "scope_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": "PROJECT",
                                            "right_hand_side": {
                                                "uuid_list": [
                                                    projectUUID
                                                ]
                                            }
                                        }
                                    ],
                                    "entity_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "blueprint"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "environment"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "marketplace_item"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "runbook"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "vm"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            },
                                            "left_hand_side": {
                                                "entity_type": "user"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            },
                                            "left_hand_side": {
                                                "entity_type": "user_group"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "app_showback"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "description": ""
                },
                "metadata": {
                    "kind": "access_control_policy"
                },
                "operation": "ADD"
            }
        ]
    }
}

# We launch the update
url="https://%s:9440/api/nutanix/v3/projects_internal/%s" % (pc_ip,projectUUID)

response = requests.put(url, json=payload, headers=headers, verify=False, auth=(pc_user, pc_pwd))
response_data=response.json()

print("Project created and updated successfully!")

# DO NOT REMOVE - Used by Self-Service and other scripts
print("ProjectUUID=" + projectUUID)

exit(0)