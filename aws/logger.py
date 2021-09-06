import time
from halo import Halo

def log_checker (executions, ssm):
    '''
    1. Ensure all run command invocations are complete
    2. Extract logs for failed invocations and append to vm_logs
    3. log_checker() is consumed by invoke_linux() / invoke_windows()
    '''

    # Create list for appending logs
    vm_logs = []

    print('----')
    print('Waiting for invocations to be complete')
    num_done = 0

    spinner=Halo(text = f'[0/{len(executions)}] Done', spinner='clock')
    spinner.start()

    while True:
        for instance_id, command_id in executions:
            status = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)["Status"]
            if status!='Pending' and status!='InProgress':
                num_done += 1
        spinner.text=f'[{num_done}/{len(executions)}] Done'
        if num_done == len(executions):
            break;

        num_done = 0
        time.sleep(1)

    spinner.stop()
    print("Complete!")

    for instance_id, command_id in executions:
        try:
            vm_log = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
            # this does not work - need to find object returned and how to access status
            if vm_log["Status"]=='Failed' or vm_log["Status"]=='TimedOut':
                vm_logs.append(vm_log)
        except:
            print (f"Check if run command was invoked for {instance_id}")

    return (vm_logs)
