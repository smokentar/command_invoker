from shutil import rmtree
import concurrent.futures

from run_command_windows import invoke_windows
from run_command_linux import invoke_linux
from script_selector import script_selector

import os
import json
import click
import boto3
import jinja2

@click.command()
@click.option('--vmlist/--no-vmlist', required=True, help='Only instances from vmlist / All tagged instances',)
@click.option('--profile', required=True, help='AWS profile to establish a session with')

def main(vmlist, profile):
    '''
    1. Establish a session using an AWS profile
    2. Call invoke_linux() / invoke_windows() with the session
    '''

    # Location of scripts
    scripts_path = "../scripts"

    # Split scripts in two lists
    linuxList, windowsList = script_selector(scripts_path)
    print (linuxList)
    print (windowsList)

    boto3.setup_default_session(profile_name=profile)

    # Check if logs folder exists and re-create it
    if os.path.exists('logs'):
        rmtree('logs')
    os.mkdir('logs')


    # For vmlist flag read instance ids from vmlist.txt and append to list
    if vmlist:
        with open ('vmlist.txt', 'r') as f:
            instance_list = [line.strip() for line in f]

    # For no-vmlist flag define an empty list
    else:
        instance_list = []

    ec2 = boto3.resource('ec2', region_name='eu-west-1')
    ssm = boto3.client('ssm', region_name='eu-west-1')

    # Get the objects of instances from vmlist.txt
    if len(instance_list) > 0:
        instances = [instance for instance in ec2.instances.all() if instance.id in instance_list]

    # Get the objects of all instances in the account
    else:
        instances = ec2.instances.all()

    for script in windowsList:
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../scripts/windows"))

        ps_template = j2env.get_template(script)
        ps_script = str(ps_template.render())

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        future_get_vms = {
            executor.submit(invoke_windows, instance_list, ps_script, script, ec2, ssm, instances)
        }

        # Extract logging information for each instance and place under logs/<instance-id>
        # Returned object from future.result() is a dict
        for future in concurrent.futures.as_completed(future_get_vms):
            for vm_log in future.result():
                instance_id = vm_log['InstanceId']
                if not os.path.exists(f'logs/{instance_id}'):
                    os.mkdir(f'logs/{instance_id}')

                with open (f"logs/{instance_id}/{script}.log", "w+") as logfile:
                    logfile.write(json.dumps(vm_log))


    for script in linuxList:
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../scripts/linux"))

        sh_template = j2env.get_template(script)
        sh_script = str(sh_template.render())

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        future_get_vms = {
            executor.submit(invoke_linux, instance_list, sh_script, script, ec2, ssm, instances)
        }

        # Extract logging information for each instance and place under logs/<instance-id>
        # Returned object from future.result() is a dict
        for future in concurrent.futures.as_completed(future_get_vms):
            for vm_log in future.result():
                instance_id = vm_log['InstanceId']
                if not os.path.exists(f'logs/{instance_id}'):
                    os.mkdir(f'logs/{instance_id}')

                with open (f"logs/{instance_id}/{script}.log", "w+") as logfile:
                    logfile.write(json.dumps(vm_log))

if __name__ == '__main__':
    main()
