#from __future__ import division
import json
import logging
import socket

import subprocess

import os
import urllib.request

import re


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def ask(question):
    answer = ""
    while (answer!='N') & (answer!='Y'):
        answer = input(question + bcolors.OKGREEN + " Y" + bcolors.ENDC + "es "+bcolors.FAIL+"N"+ bcolors.ENDC +"o type Y or N and press enter\n")
        answer=answer.upper()
    return answer=='Y'



print(bcolors.OKGREEN + "Warning: No active frommets remain. Continue?"  + bcolors.ENDC)


def installPsUtil():
    print("installing ps util it can take a while ...")
    os.system('sudo python3.5 -m pip install psutil')
    print( bcolors.OKGREEN+"INSTALLED"+ bcolors.ENDC )
    pass

def isntallAdafruitPWM():
    print("installing adafruit-pca9685 it can take a while ...")
    os.system('sudo python3.5 -m pip install adafruit-pca9685')
    print( bcolors.OKGREEN+"INSTALLED"+ bcolors.ENDC )
    pass


def takeUserName(server,port,token):
    try:
        url="http://{}:{}/api/{}/rest/v1/user/getUserName/".format(server,port,token)

        response=urllib.request.urlopen(url)
        if response.getcode()!=200:
            return None
        userName = response.read().decode('utf-8')
        if len(userName)<20:
            return userName
        else:
            return None
    except:
        return None


def checkIfTaken(server, port, token, toCheck, param):
        url="http://{}:{}/api/{}/rest/v1/user/{}/{}/".format(server,port,token,param,toCheck)
        response=urllib.request.urlopen(url)
        if response.getcode()!=200:
            return None
        ret = response.read().decode('utf-8')
        if ret=="false":
            return toCheck
        else:
            print("{} is already taken".format(toCheck))
            return None


def updateConf():

    with open("conf.json", "r") as jsonFile:
        data = json.load(jsonFile)

    token = None
    name=None
    deviceId = None



    if data['server'].get('token',None)!=None:
        if not ask("there is already provided token [{}] would You like to replace it ?".format(data['server']['token'])):
            token=data['server']['token']

    ip=data['server']['ip']
    port=data['server']['port']


    if token!=None:
        userName=takeUserName(ip,port,token.strip())
    else:
        userName=None

    while userName==None:
        token =input("Provide Token and press enter\n").strip()
        userName=takeUserName(ip,port,token)
        if userName==None:
            print(bcolors.FAIL + "Token was not found :( " + bcolors.ENDC)


#------------------ NAME ---------------------------------------
    if data['server'].get('name', None) != None:
        if not ask("there is already provided name of device [{}] would You like to replace it ?".format( data['server']['name'])):
            name = data['server']['name']


    while name == None:
        name = input("Provide Name ( for example RicksRaspberry only alfanumeric) and press enter\n").strip()
        name = re.sub(r'\W+', '', name)
        if len(name) == 0:
            name = None
        else:
            name=checkIfTaken(ip,port,token,name,"isDeviceNameTaken")
#------------------- ID -----------------------------------------

    if data['server'].get('deviceId', None) != None:
        if not ask("there is already provided deviceId of device [{}] would You like to replace it ?".format(data['server']['deviceId'])):
            deviceId = data['server']['deviceId']

    while deviceId == None:
        deviceId = input("Provide deviceId ( only numbers) and press enter\n").strip()
        if len(deviceId) == 0:
            deviceId = None
        else:
            try:
                deviceId=int(deviceId)
                deviceId = checkIfTaken(ip, port, token, deviceId, "isDeviceIdTaken")
            except:
                deviceId=None

#------------------------ end deviceId---------------------------------

    data['server']['token']=token
    data['server']['name']=name
    data['server']['deviceId']=deviceId



    with open("conf.json", "w") as jsonFile:
        json.dump(data, jsonFile,indent="  ")

    print("Hello "+bcolors.FAIL+userName+bcolors.ENDC+" !! Your settings was saved to conf.json :")
    print("token: {}".format(token))
    print("name: {}".format(name))
    print("deviceId: {}".format(deviceId))
    pass


try:


    if ask("Would You like to install psutil - it's needed to make application manager works properly ?"):
       installPsUtil()

    if ask("Would You like to install  adafruit-pca9685 - it's with playting with PWM servo mechanism device ?"):
        isntallAdafruitPWM()

    if ask("Would You like to update your configuration ? - its needed for proper connecting remoteme to server"):
        updateConf()

    os.system('chmod +x runme.sh')
    os.system('chmod +x remoteme')

    print( bcolors.OKGREEN+"INSTALATION finish you can run remoteme by './runme.sh'"+ bcolors.ENDC )
except:
    print(bcolors.FAIL + "Error while isntalation :( (Are You sudo ?)" + bcolors.ENDC)