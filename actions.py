# Put here all the actions that can be used by the #>A:<action name>#" calls
    
import ntnx_vmm_py_client
from functions import *
import requests
from base64 import b64encode
import os
import uuid

# ====================================================================================================
# deleteVM
# ====================================================================================================
# This function delete VM identified in the variables
def deleteVM(variables):

    # Configure the client
    sdkConfig = confSDKClient(variables['PC'], variables['PCUser'], variables['PCPassword'])
    client = ntnx_vmm_py_client.ApiClient(configuration=sdkConfig)
    vm_api = ntnx_vmm_py_client.VmApi(api_client=client)
  

    try:
        api_response = vm_api.get_vm_by_id(extId=variables['VMUUID'])
    except ntnx_vmm_py_client.rest.ApiException as e:
        print(e)

    # Extract E-Tag Header
    etag_value = ntnx_vmm_py_client.ApiClient.get_etag(api_response)

    try:
        api_response = vm_api.delete_vm_by_id(extId=variables['VMUUID'], if_match=etag_value)
    except ntnx_vmm_py_client.rest.ApiException as e:
        print(e)

    return True

# ====================================================================================================
# deployBlueprint
# ====================================================================================================
# To Do : Migrate to v4 API/SDK when available
def deployBlueprint( variables ):
    # Get Blueprint ID
    url = "https://%s:9440/api/nutanix/v3/blueprints/list" % variables['PC']
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    payload = {
        "kind": "blueprint"
    }
    response = requests.post(url,json=payload,verify=False,auth=(variables['PCUser'], variables['PCPassword']),headers=headers)
    response_data = json.loads(response.text)

    jsonpath_expr = parse('$.entities[?(@.metadata.name =~ "source$")].metadata.uuid')

    for match in jsonpath_expr.find(response_data):
        bpUuid=match.value

    # We clone it
    url = "https://%s:9440/api/nutanix/v3/blueprints/%s/clone" % (variables['PC'], bpUuid)
    payload={
        "blueprint_name": "bp-blankvm-prd"+variables['Vlanid'],
        "metadata": {
            "kind": "blueprint",
            "uuid": str(uuid.uuid4()),
            }
        }
    response = requests.post(url,json=payload,verify=False,auth=(variables['PCUser'], variables['PCPassword']),headers=headers)


    return True

