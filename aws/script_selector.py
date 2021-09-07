import os

def script_selector(scripts_path):
    '''
    Return linuxList and windowsList with scripts to execute based on user input
    This function is complete chaos
    '''

    # Create lists of linux / windows scripts
    linuxList = os.listdir(f'{scripts_path}/linux')
    windowsList = os.listdir(f'{scripts_path}/windows')

    # Display linux / windows scripts available
    print ('\n')

    print ('Linux catalog:')
    print ('----')
    for number in range (len(linuxList)):
        print ('{}. {}'.format(number+1, linuxList[number]))

    print ('\n')

    print ('Windows catalog:')
    print ('----')
    for number in range (len(windowsList)):
        print ('{}. {}'.format(number+1, windowsList[number]))

    print ('\n')

    # Prompt for selection
    linuxSelection = input('Select Linux scripts by comma-separated number inputs: ')
    windowsSelection = input('Select Windows scripts by comma-separated number inputs: ')

    linuxEvaluator = linuxSelection.split(',')
    windowsEvaluator = windowsSelection.split(',')

    # Helper list to identify items for removal
    remover = []

    for script in linuxList:
        if str(linuxList.index(script)+1) not in linuxEvaluator:
            remover.append(script)
    for script in remover:
        linuxList.remove(script)

    # Clear helper list for next iteration
    remover.clear()

    for script in windowsList:
        if str(windowsList.index(script)+1) not in windowsEvaluator:
            remover.append(script)

    for script in remover:
        windowsList.remove(script)

    return (linuxList, windowsList)
