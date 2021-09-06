import time
from halo import Halo

def log_checker (executions):
    '''
    1. Ensure all run command invocations are complete
    2. Extract logs for failed invocations and append to vm_logs
    3. log_checker() is consumed by get_vms_offboard()
    '''

    # Create list for appending logs
    vm_logs = []

    print ('----')
    print ('Waiting for invocations to be complete')
    num_done = 0

    spinner = Halo(text = f'[0/{len(executions)}] Done', spinner='clock')
    spinner.start()

    while True:
        for vm, execution in executions:
            if execution.done():
                num_done += 1

        spinner.text = f"[{num_done}/{len(executions)}] Done"
        if num_done == len(executions):
            break

        num_done = 0
        time.sleep(1)

    spinner.stop()
    print("Complete!")

    for vm_name, poller in executions:
        # Only fetch failed commands for windows
        # Fetch stdout + stderr on linux (cannot be accessed separately)
        # Can search the string with regex to filter
        try:
            # stderr
            windowsLog = poller.result().value[1]
            if (windowsLog.message):
                vm_logs.append ((vm_name, windowsLog.message))
        except IndexError:
            # stdout + stderr
            linuxLog = poller.result().value[0]
            vm_logs.append ((vm_name, linuxLog.message))
        except Exception as e:
            print (f"Execution failed for {vm_name} - investigate log:\n{e}\n")

    return (vm_logs)
