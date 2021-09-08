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
@click.option('--vmlist / --tag', required=True, help='Only instances from vmlist / Tagged instances')
@click.option('--profile', required=True, help='AWS profile to establish a session with')
@click.option('--tag_key', required=False, help='Key of tag')
@click.option('--tag_value', required=False, help="Value of tag")

def main(vmlist, tag_key, tag_value, profile):
    '''
    1. Establish a session using an AWS profile
    2. Call invoke_linux() / invoke_windows() with the session
    '''

    # Location of scripts
    scripts_path = "scripts"
    provider = "aws"

    # This is passed to the run_command builders
    instances = []

    # Split scripts in two lists
    linuxList, windowsList = script_selector(scripts_path)
    print (linuxList)
    print (windowsList)

    boto3.setup_default_session(profile_name=profile)

    # Check if logs folder exists and re-create it
    if os.path.exists(f'{provider}/logs'):
        rmtree(f'{provider}/logs')
    os.mkdir(f'{provider}/logs')


    # For vmlist flag read instance ids from vmlist.txt and append to list
    if vmlist:
        with open (f'{provider}/vmlist.txt', 'r') as f:
            instance_list = [line.strip() for line in f]

    # For tag flag define an empty list
    else:
        instance_list = []

    ec2 = boto3.resource('ec2', region_name='eu-west-1')
    ssm = boto3.client('ssm', region_name='eu-west-1')

    # Get the objects of instances from vmlist.txt
    if len(instance_list) > 0:
        for instance in ec2.instances.all():
            if instance.id in instance_list:
                instances.append(instance)

    # Get the objects of tagged instances
    else:
        for instance in ec2.instances.all():
            if instance.tags is not None:
                for tag in instance.tags:
                    if f'{tag_key}' in tag['Key'] and f'{tag_value}' in tag['Value']:
                        instances.append(instance)

    for script in windowsList:
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=f'{scripts_path}/windows'))

        ps_template = j2env.get_template(script)
        ps_script = str(ps_template.render())

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        future_get_vms = {
            executor.submit(invoke_windows, ps_script, script, ec2, ssm, instances)
        }

        # Extract logging information for each instance and place under logs/<instance-id>
        # Returned object from future.result() is a dict
        for future in concurrent.futures.as_completed(future_get_vms):
            for vm_log in future.result():
                instance_id = vm_log['InstanceId']
                if not os.path.exists(f'{provider}/logs/{instance_id}'):
                    os.mkdir(f'{provider}/logs/{instance_id}')

                with open (f'{provider}/logs/{instance_id}/{script}.log', 'w+') as logfile:
                    logfile.write(json.dumps(vm_log))


    for script in linuxList:
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=f'{scripts_path}/linux'))

        sh_template = j2env.get_template(script)
        sh_script = str(sh_template.render())

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        future_get_vms = {
            executor.submit(invoke_linux, sh_script, script, ec2, ssm, instances)
        }

        # Extract logging information for each instance and place under logs/<instance-id>
        # Returned object from future.result() is a dict
        for future in concurrent.futures.as_completed(future_get_vms):
            for vm_log in future.result():
                instance_id = vm_log['InstanceId']
                if not os.path.exists(f'{provider}/logs/{instance_id}'):
                    os.mkdir(f'{provider}/logs/{instance_id}')

                with open (f'{provider}/logs/{instance_id}/{script}.log', 'w+') as logfile:
                    logfile.write(json.dumps(vm_log))

if __name__ == '__main__':
    main()
