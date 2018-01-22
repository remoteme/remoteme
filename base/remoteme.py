import socket
import threading

import struct

import remotemeMessages
import remotemeStruct
import logging

from remotemeMessages import getUserMessage


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class RemoteMe(metaclass=Singleton):
    pass

    __userMessageListeners=[]
    __userSyncMessageListeners=[]


    __socketObj = None
    __ownId = None
    __threadRead = None

    def __init__(self):
        self.__logger = logging.getLogger('remoteMe.RemoteMe')
        self.__logger.info('creating an instance of RemoteMe')

    def __readFromSocket(self):
        while self.__socketObj is not None :
            try:
                header = self.__socketObj.recv(4)
                if (len(header) == 4):
                    [messageType, size] = struct.unpack(">hh", header)
                    messageType = remotemeStruct.MessageType(messageType)
                    data = self.__socketObj.recv(size)
                    if (len(data) == size):
                        if (messageType == remotemeStruct.MessageType.USER_MESSAGE):
                            [userMessageSettings, receiverDeviceId, senderDeviceId, messageId, data] = struct.unpack(
                                ">Bhhh{0}s".format(size - remotemeStruct.USER_DATA_HEADEARS_SIZE), data)
                            userMessageSettings = remotemeStruct.UserMessageSettings(userMessageSettings)#for later use
    
                            if (self.__ownId==receiverDeviceId):
                                self.__onUserMessage(userMessageSettings,senderDeviceId, messageId, data)
                            else:
                                print('PYTHON wrong deviceId :{} '.format(receiverDeviceId))
                        elif messageType == remotemeStruct.MessageType.USER_SYNC_MESSAGE:
                            self.__logger.info("expected size of bytes {} data length:{}".format(size - remotemeStruct.USER_SYNC_DATA_HEADEARS_SIZE,len(data)));
                            [receiverDeviceId, senderDeviceId, messageId, data] = struct.unpack(
                                ">hhQ{0}s".format(size - remotemeStruct.USER_SYNC_DATA_HEADEARS_SIZE), data)
    
                            if (self.__ownId==receiverDeviceId):
                                self.__onSyncMessage(senderDeviceId, messageId, data)
                            else:
                                print('PYTHON wrong deviceId :{} '.format(receiverDeviceId))
                        else:
                            print('PYTHON wrong data type {} '.format(messageType))
            except:
                self.__logger.exception("error while processing message")
                exit(0)
        print("PYTHON end loop")




    def __toHexString(self,array):
        return (''.join('{:02x} '.format(x) for x in array))

    def __onUserMessage(self,userMessageSettings,senderDeviceId,messageId,data):
        self.__logger.debug("got user sender deviceId:{} datalen:{} data: {} ".format(senderDeviceId , len(data),self.__toHexString(data)))
        for listener in self.__userMessageListeners:
            listener(senderDeviceId,data)

    def __onSyncMessage(self,senderDeviceId,messageId, data):
        self.__logger.debug("got user senc sender senderDeviceId:{} messageId:{} datalen:{} data: {} ".format(senderDeviceId, messageId, len(data),self.__toHexString(data)))
        response=None

        for listener in self.__userSyncMessageListeners:
            response = listener(senderDeviceId, data)

        if response is None:
            response=[]

        responseMessage = remotemeMessages.getSyncResponseMessage(messageId,response)
        self.__send(responseMessage)



    def __send(self,message):
        self.__socketObj.sendall(message)



    def __exit__(self, exc_type, exc_value, traceback):
        self.__logger.info("Exit remoteme python with id {}".format(self.__ownId))
        if self.__socketObj is not None:
            self.__socketObj.close()
            self.__socketObj = None

        if self.__threadRead is not None:
            self.__threadRead.join(1000)


    def startRemoteMe(self,sysargv):
        if (len(sysargv)>=4):
            parentId = int(sysargv[1])
            ownId = int(sysargv[2])
            port = int(sysargv[3])
            name="python script"
            if len(sysargv)==5:
                name=sysargv[4]

            self.startRemoteMeDirect(port,parentId,ownId,name)

        else:
            self.__logger.info("usable parentId ownId port deviceName")
            self.__logger.info("got parameters {} : {}".format(len(sysargv), sysargv))
            exit(1)


    def startRemoteMeDirect(self, port, parentId, ownId,name):
        if self.__socketObj is not None:
            self.__logger.warning("Remote Me already started")
            return


        self.__logger.info("starting remogemeMe port:{} parentId:{} ownId:{} name:{}".format(port, parentId, ownId,name))
        self.__ownId = ownId

        self.__socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socketObj.connect(("localhost", port))

        self.__threadRead = threading.Thread(target=self.__readFromSocket)
        self.__threadRead.daemon = True
        self.__threadRead.start()

        self.__send(remotemeMessages.getRegisterLeafDeviceMessage(parentId, self.__ownId, name,
                                                                  remotemeStruct.LeafDeviceType.LD_EXTERNAL_SCRIPT))

    def addUserMessageListener(self, function):
        self.__userMessageListeners.append(function)

    def addUserSyncMessageListener(self, function):
        self.__userSyncMessageListeners.append(function)

    def sendUserMessage(self,receiveDeviceId,data):
        self.__send(remotemeMessages.getUserMessage(remotemeStruct.UserMessageSettings.NO_RENEWAL, receiveDeviceId, self.__ownId, 0, data))

    def logServerInfo(self, message):
        self.__send(remotemeMessages.getLogMessage(remotemeStruct.LogLevel.INFO, message))

    def logServerWarn(self, message):
        self.__send(remotemeMessages.getLogMessage(remotemeStruct.LogLevel.WARN, message))

    def logServerError(self, message):
        self.__send(remotemeMessages.getLogMessage(remotemeStruct.LogLevel.ERROR, message))

    def wait(self):
        self.__threadRead.join()

