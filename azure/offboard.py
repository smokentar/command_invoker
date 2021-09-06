from run_command_windows import invoke_windows
from run_command_linux import invoke_linux

from script_selector import script_selector

import concurrent.futures
from shutil import rmtree

import os
import json
import click
import jinja2
import subprocess

@click.command()
@click.option('--vmlist/--no-vmlist', required=True, help='Only VMs from vmlist / All tagged VMs',)

def main(vmlist):
    """
    1. Prompt for login to a tenant
    2. Call invoke_linux() / invoke_windows() with the session
    """

    # Location of scripts
    scripts_path = "../scripts"

    # Split scripts in two lists
    linuxList, windowsList = script_selector(scripts_path)
    print (linuxList)
    print (windowsList)

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

    # Prompt for tenant login
    process = subprocess.Popen(["az", "login"])
    process.wait()

    for script in windowsList:
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../scripts/windows"))

        ps_template = j2env.get_template(script)
        ps_script = ps_template.render().split("\n")

        # Keep the workers at 4 to avoid issues with concurrency
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        future_get_vms = {
            executor.submit(invoke_windows, instance_list, ps_script, script)
        }

        # Extract logging information for each VM and place under logs/<VM_name>
        # Returned object from future.result() is a dict
        for future in concurrent.futures.as_completed(future_get_vms):
            for vm_name, result in future.result():
                if not os.path.exists(f'logs/{vm_name}'):
                    os.mkdir(f'logs/{vm_name}')

                with open (f"logs/{vm_name}/{script}.log", "w+") as logfile:
                    logfile.write(json.dumps(result))

    for script in linuxList:
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../scripts/linux"))

        sh_template = j2env.get_template(script)
        sh_script = sh_template.render().split("\n")

        # Keep the workers at 4 to avoid issues with concurrency
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        future_get_vms = {
            executor.submit(invoke_linux, instance_list, sh_script, script)
        }

        # Extract logging information for each VM and place under logs/<VM_name>
        # Returned object from future.result() is a dict
        for future in concurrent.futures.as_completed(future_get_vms):
            for vm_name, result in future.result():
                if not os.path.exists(f'logs/{vm_name}'):
                    os.mkdir(f'logs/{vm_name}')

                with open (f"logs/{vm_name}/{script}.log", "w+") as logfile:
                    logfile.write(json.dumps(result))

if __name__ == '__main__':
    main()
