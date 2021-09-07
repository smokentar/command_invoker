from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.common.client_factory import get_client_from_cli_profile

from logger import log_checker

def invoke_linux(instance_list, sh_script, script, tag_key, tag_value):
    """
    1. Fetch all subscriptions that user has access to
    2. Iterate over vmlist.txt or all supported instances based on tag
    3. Invoke run_command on the discovered VMs
    """

    # List for command invocations
    executions = []

    # List for subscriptions
    subscriptions = []

    # List for VM objects
    vms = []

    # Build the run command arguments
    run_command_sh = {
        'command_id': 'RunShellScript',
        'script': sh_script
    }

    # Get all subscriptions available to user and place them in a list
    subscription_client = get_client_from_cli_profile(SubscriptionClient)
    subscription = next(subscription_client.subscriptions.list())

    subscriptions.append (subscription.subscription_id)

    # Iterate over the subscriptinos and run commands
    for subscription in subscriptions:

        compute_client = (get_client_from_cli_profile(
            ComputeManagementClient, subscription_id=subscription
        ))
        # Get the objects of VMs from vmlist.txt
        if len(instance_list) > 0:
            for vm in compute_client.virtual_machines.list_all():
                if vm.name in instance_list:
                    vms.append(vm)

        # Get the objects of tagged VMs in the subscription
        else:
            for vm in compute_client.virtual_machines.list_all():
                if vm.tags is not None:
                    if f'{tag_key}' in vm.tags and vm.tags[f'{tag_key}'].lower() == f'{tag_value}':
                        vms.append(vm)

        print ('\n')
        print (f'[{script}]')
        print ('----')

        for virtual_machine in vms:
            # VM ID format: '/subscriptions/subscription_id/resourceGroups/resource_group/providers/Microsoft.Compute/virtualMachines/vm_name'
            # Split VM ID string into a list
            temp_placeholder = virtual_machine.id.split('/')
            # Access resource_group
            resource_group = temp_placeholder[4]
            try:
                if "windows" not in virtual_machine.storage_profile.os_disk.os_type.lower():
                    print (f"Linux: {virtual_machine.name}")
                    poller = compute_client.virtual_machines.begin_run_command(resource_group, virtual_machine.name, run_command_sh)
                    # Place exection details in a list
                    executions.append((virtual_machine.name, poller))
            except Exception as e:
                print (f"Execution failed for {virtual_machine.name} - investigate log:\n{e}\n")

    # Call log_checker() to extract failure logs
    vm_logs = log_checker(executions)

    return (vm_logs)
