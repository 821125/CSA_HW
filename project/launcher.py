"""Launcher"""

import subprocess

PROCESS = []

while True:
    ACTION = input('use q for exit, s for run server and clients, x - close all: ')

    # if ACTION == 'q':
    #     break
    # elif ACTION == 's':
    #     PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
    #     PROCESS.append(subprocess.Popen('python client.py -n test1', creationflags=subprocess.CREATE_NEW_CONSOLE))
    #     PROCESS.append(subprocess.Popen('python client.py -n test2', creationflags=subprocess.CREATE_NEW_CONSOLE))
    #     PROCESS.append(subprocess.Popen('python client.py -n test3', creationflags=subprocess.CREATE_NEW_CONSOLE))
    #
    # elif ACTION == 'x':
    #     while PROCESS:
    #         VICTIM = PROCESS.pop()
    #         VICTIM.kill()

    if ACTION == 'q':
        break
    elif ACTION == 's':
        clients_count = int(input('Input number of clients: '))
        # Run server
        PROCESS.append(subprocess.Popen('python server_script.py.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        # Run clients
        for i in range(clients_count):
            PROCESS.append(subprocess.Popen(f'python client.py -n test{i + 1}',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            PROCESS.pop().kill()
