import time

from logger import log_checker

def invoke_windows(ps_script, script, ec2, ssm, instances):
    """
    1. Iterate over vmlist.txt or instances based on tag
    2. Ensure they report to SSM
    3. Invoke an SSM run command
    """

    # List for appending command invocations
    executions = []

    print ('\n')
    print (f'[{script}]')
    print ('----')

    for instance in instances:
        try:
            try:
                # Get the instance SSM status
                status = ssm.describe_instance_associations_status(InstanceId=instance.id)['InstanceAssociationStatusInfos'][0]['Status']
            except IndexError:
                status = "Not enrolled"

            if (instance.state['Name'] == "running" and status == "Success"):
                if instance.platform == 'windows':
                    print ('Windows: ' + instance.id)
                    try:
                        run_command_ps = ssm.send_command (
                            InstanceIds = [instance.id],
                            DocumentName = 'AWS-RunPowerShellScript',
                            Parameters = {
                                'commands':[
                                    ps_script
                                ]
                            },
                        )
                        command_id = run_command_ps['Command']['CommandId']
                    except Exception as e:
                        raise e
                    # Extract response from each run command invocation
                    # Sleep for half a second to ensure the response is logged to AWS before fetching
                    # append instance.platform for identification to be passed into log_checker
                    executions.append((instance.id, command_id))
                    time.sleep(0.5)
            else:
                print (instance.id + ' -> Stopped or not reporting to SSM')

        except Exception as e:
            print (f"Execution failed for {instance.id} - investigate log:\n{e}\n")

    # Call log_checker() to extract failure logs
    vm_logs = log_checker(executions, ssm)

    return (vm_logs)
