import signal
import subprocess
import os
import re
import threading
import psutil
import signal
import time

from psutil import NoSuchProcess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printOK(toPrint):
    print(bcolors.OKGREEN+toPrint+bcolors.ENDC)


def printBLUE(toPrint):
    print(bcolors.OKBLUE+toPrint+bcolors.ENDC)

def printWARNING(toPrint):
    print(bcolors.WARNING+toPrint+bcolors.ENDC)

def printERROR(toPrint):
    print(bcolors.FAIL+toPrint+bcolors.ENDC)

remotemeThread = None
remotemeThreadId = None
remotemeThreadChildId=[]
lastSignalReceived = None

def handler(signum, frame):
    global lastSignalReceived
    lastSignalReceived = time.time()



# def getProcess(command):
#     ret=[]
#     p = re.compile('(\d+)_(.+)\n')
#     for x in os.popen("ps -aux |grep '"+command+"' | awk ' { print $2 \"_\" $11 \" \" $12 \" \" $13  }'"):
#         if (p.match(x)):
#             m = p.search(x)
#             if (command.strip() == m.group(2).strip()):
#                 return int(m.group(1))
#
#
#     return 0




def runProgram(command):
    subprocess.call(command)


def killRemoteme():
    global remotemeThreadChildId
    global remotemeThreadId
    global remotemeThread
    try:
        printWARNING("------------------ killing remoteme -------------------")
        processIds=[]
        if remotemeThreadId:
            processIds.append(remotemeThreadId)
        processIds.extend(remotemeThreadChildId)

        printOK("Going to kill {}  processes with  pids: {}".format(len(processIds),processIds))
        for processId in processIds:
            try:
                process = psutil.Process(processId)
                if process.is_running():
                    printOK("sending terminate to process {}".format(processId))
                    os.kill(processId, signal.SIGTERM)
                    waitTillNotRunning(process)
                    if process.is_running():
                        printWARNING("process is still running after send SIGTERM  -- sending kill ")
                        os.kill(processId, signal.SIGKILL)
                        waitTillNotRunning(process)
                        if process.is_running():
                            printWARNING("process is still running still running after trying to kill -- terminate ")
                            process.terminate()
                            waitTillNotRunning(process)
                            if process.is_running():
                                printWARNING("process is still running after trying to terminate -- kill ")
                                process.kill()
                                waitTillNotRunning(process)

                    if process.is_running():
                        printERROR("processes {} is stil RUNNING".format(processId))
                    else:
                        printOK("processes {} was terminated".format(processId))

                else:
                    printOK("processes {} is already not running".format(processId))
            except NoSuchProcess:
                printOK("processes {} is already dead".format(processId))
            except:
                printERROR("erorr while killing process with id {} (probably already dead)".format(processId))

    except:
        printERROR("erorr while killing remoteme")
    finally:
        printOK("finishing killing")
        remotemeThreadChildId = []
        remotemeThreadId = None
        if remotemeThread:
            remotemeThread.join()
        remotemeThread = None
        printOK("----- remoteme me has been killed-------")


def waitTillNotRunning(process,timeToWait=3):
    try:
        process.wait(timeout=timeToWait)
    except:
        pass



def addExisitingChildrensOfRemoteme():
    global remotemeThreadId
    global remotemeThreadChildId
    added=False
    try:
        if remotemeThreadId:
            parent = psutil.Process(remotemeThreadId)

            children = parent.children(recursive=True)
            for process in children:
                if process.pid not in remotemeThreadChildId:
                    printBLUE("adding new pid  child {}".format( process.pid))
                    remotemeThreadChildId.append( process.pid)
                    added=True

            if added:
                print("collected new child process now there is {} child processes".format(len(remotemeThreadChildId)))
    except:
            print("error collecting child")
    finally:
        pass

def runRemoteme():
    global remotemeThread
    global remotemeThreadId
    global lastSignalReceived

    killRemoteme()
    lastSignalReceived=time.time()

    remotemeThread = threading.Thread(target=runProgram, args=["./remoteme"])
    remotemeThread.daemon = False
    remotemeThread.start()
    time.sleep(1)
    parent = psutil.Process(psutil.Process().pid)
    children = parent.children(recursive=True)
    for process in children:
        if (process.name()=='remoteme'):
            remotemeThreadId=process.pid
            printBLUE("Remoteme run with pid:{}".format(remotemeThreadId))



#for pair in getProcess("stream\|python\|0"):
 #   print(pair)

printOK("Running remoteme Manager my pid is :{}".format(psutil.Process().pid))

signal.signal(signal.SIGUSR1, handler)


try:


    for x in range(0, 10000):
        addExisitingChildrensOfRemoteme()
        if (remotemeThread and remotemeThread.is_alive()):
            pass #print("remoteme me pid {} ".format(remotemeThreadId))
        else:
            runRemoteme()



        if lastSignalReceived+20<time.time():
            printWARNING("didnt get signlal from remoteme for longer then 20s - killing and restarting")
            runRemoteme()

        time.sleep(2)

finally:
    killRemoteme()



