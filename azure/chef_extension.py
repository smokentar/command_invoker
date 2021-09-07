import click
import subprocess

from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.common.client_factory import get_client_from_cli_profile

@click.command()
@click.option('--vmlist/--no-vmlist', required=True, help='Only VMs from vmlist / All tagged VMs',)
@click.option('--uninstall/--describe', required=True, help='Uninstall the chef extension / Check if chef extension exists',)

def main(vmlist, uninstall):
    '''
    Standalone script to remove the chef extension for legacy clients not migrated to the latest Azure Conductor AO
    '''

    subscriptions = []

    if vmlist:
        with open ('vmlist.txt', 'r') as f:
            instance_list = [line.strip() for line in f]

    # For no-vmlist flag define an empty list
    else:
        instance_list = []

    process = subprocess.Popen(["az", "login"])
    process.wait()

    subscription_client = get_client_from_cli_profile(SubscriptionClient)
    subscription = next(subscription_client.subscriptions.list())

    subscriptions.append (subscription.subscription_id)

    for subscription in subscriptions:

        compute_client = (get_client_from_cli_profile(
            ComputeManagementClient, subscription_id=subscription
        ))
        # Get the objects of VMs from vmlist.txt
        if len(instance_list) > 0:
            print ('List provided, proceeding with specified instances:')
            print ('----')
            vms = [vm for vm in compute_client.virtual_machines.list_all() if vm.name in instance_list]

        # Get the objects of all VMs in the subscription
        else:
            print ('No list provided, proceeding with all supported instances:')
            print ('----')
            vms = compute_client.virtual_machines.list_all()

        for virtual_machine in vms:
            if virtual_machine.tags is not None:
                if "TagKey" in virtual_machine.tags and virtual_machine.tags["TagKey"].lower() == "TagValue":
                    # VM ID format: '/subscriptions/subscription_id/resourceGroups/resource_group/providers/Microsoft.Compute/virtualMachines/vm_name'
                    temp_placeholder = virtual_machine.id.split('/') # Split VM ID string into a list
                    resource_group = temp_placeholder[4] # Access resource_group
                    if uninstall:
                        if "windows" in virtual_machine.storage_profile.os_disk.os_type.lower():
                            process = subprocess.call(["az", "vm", "extension", "delete", "-g", resource_group, "--vm-name", virtual_machine.name, "-n", "ChefClient", "--no-wait"])
                        else:
                            process = subprocess.call(["az", "vm", "extension", "delete", "-g", resource_group, "--vm-name", virtual_machine.name, "-n", "LinuxChefClient", "--no-wait"])
                        print (f'Removing chef extension on {virtual_machine.name}')
                    else:
                        process = subprocess.call(["az", "vm", "extension", "list", "-g", resource_group, "--vm-name", virtual_machine.name, "--query", "[?contains(name, 'ChefClient')].id"])


if __name__ == '__main__':
    main()
