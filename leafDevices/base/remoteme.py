

import socket
import threading

import struct

import remotemeMessages
import remotemeStruct
import logging

from variables import Variables
from remoteMeDataReader import RemoteMeDataReader
from functionCaller import FunctionCaller

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class RemoteMe(metaclass=Singleton):
    pass

    __userMessageListener=None
    __userSyncMessageListener=None

    __onWebRtcConnectionChangeListeners=[]
    __onWebsocketConnectionChangeListeners = []
    __onDeviceConnectionChangeListeners = []

    __socketObj = None
    __ownId = None
    __threadRead = None
    __variables = None

    def __init__(self):
        self.__logger = logging.getLogger('remoteMe.RemoteMe')
        self.__logger.debug('creating an instance of RemoteMe')

    def __readFromSocket(self):
        concesousErrors = 0
        while self.__socketObj is not None :
            try:
                header = self.__socketObj.recv(4)
                if (len(header) == 4):
                    [messageType, size] = struct.unpack(">hh", header)
                    messageType = remotemeStruct.MessageType(messageType)
                    self.__logger.debug("got message type {} size:{}".format(messageType,size))
                    data = self.__socketObj.recv(size)
                    if (len(data) == size):
                        self.__logger.debug('Python message received')
						reader = RemoteMeDataReader(data)
                        if (messageType == remotemeStruct.MessageType.USER_MESSAGE):
							
                            userMessageSettings = remotemeStruct.UserMessageSettings( reader.readUInt8())  # for later use
                            receiverDeviceId = reader.readUInt16()
                            senderDeviceId = reader.readUInt16()
                            messageId = reader.readUInt16()
                            data = bytearray(reader.readRest())


                            if (self.__ownId==receiverDeviceId):
                                self.__onUserMessage(userMessageSettings,senderDeviceId, messageId, data)
                            else:
                                print('PYTHON wrong deviceId :{} '.format(receiverDeviceId))

                        elif (messageType == remotemeStruct.MessageType.USER_MESSAGE_WEBPAGE_TOKEN):

                            # data and type already took

                            userMessageSettings = remotemeStruct.UserMessageSettings(reader.readUInt8())  # for later use
                            receiverDeviceId = reader.readUInt16()
                            senderDeviceId = reader.readUInt16()
                            sessionId = reader.readUInt16()
                            identifier = reader.readUInt16()
                            credit = reader.readUInt16()
                            time = reader.readUInt16()
                            data = bytearray(reader.readRest())

                            if (self.__ownId == receiverDeviceId):
                                self.__onUserMessage(userMessageSettings, senderDeviceId, 0, data,sessionId,identifier,credit,time)
                            else:
                                print('PYTHON wrong deviceId :{} '.format(receiverDeviceId))

                        elif messageType == remotemeStruct.MessageType.USER_SYNC_MESSAGE:
                            self.__logger.debug("expected size of bytes {} data length:{}".format(size - remotemeStruct.USER_SYNC_DATA_HEADEARS_SIZE,len(data)));

                            receiverDeviceId=reader.readUInt16()
                            senderDeviceId=reader.readUInt16()
                            messageId=reader.readUInt64()
                            data= reader.readRest()
                            if (self.__ownId==receiverDeviceId):
                                self.__onSyncMessage(senderDeviceId, messageId, data)
                            else:
                                print('PYTHON wrong deviceId :{} '.format(receiverDeviceId))

                        elif messageType == remotemeStruct.MessageType.USER_SYNC_MESSAGE_WEBPAGE_TOKEN:
                            self.__logger.debug("expected size of bytes {} data length:{}".format(
                                size - remotemeStruct.USER_SYNC_DATA_HEADEARS_SIZE, len(data)))

                            receiverDeviceId = reader.readUInt16()
                            senderDeviceId = reader.readUInt16()

                            sessionId = reader.readUInt16()
                            identifier = reader.readUInt16()
                            credit = reader.readUInt16()
                            time = reader.readUInt16()

                            messageId = reader.readUInt64()
                            data = reader.readRest()
                            if (self.__ownId == receiverDeviceId):
                                self.__onSyncMessage(senderDeviceId, messageId, data,sessionId,identifier,credit,time)
                            else:
                                print('PYTHON wrong deviceId :{} '.format(receiverDeviceId))
                        elif messageType in (remotemeStruct.MessageType.VARIABLE_CHANGE_PROPAGATE_MESSAGE, remotemeStruct.MessageType.VARIABLE_CHANGE_PROPAGATE_MESSAGE_WEBPAGE_TOKEN):
                            self.getVariables().__onVariableChangePropagate(data,messageType)
                        elif messageType == remotemeStruct.MessageType.DEVICE_CONNECTION_CHANGE:
                            self.__onDeviceConnectionChange(data,size)
                        elif messageType == remotemeStruct.MessageType.CONNECTION_CHANGE:
                            self.__onConnectionChange(data)
                        else:
                            print('PYTHON wrong data type {} '.format(messageType))
                concesousErrors = 0
            except:
                self.__logger.exception("error while processing message")
                concesousErrors = concesousErrors+1
                if concesousErrors>5 :
                    self.__logger.error("more then 10 errors exit")
                    exit(0)
        print("PYTHON end loop")



    def getVariables(self):
        if (self.__variables == None):
            self.__variables =  Variables(self)
        return self.__variables


    def __toHexString(self,array):
        return (''.join('{:02x} '.format(x) for x in array))

    def __onUserMessage(self,userMessageSettings,senderDeviceId,messageId,data,sessionId=None,identifier=None,credit=None,time=None):
        self.__logger.debug("got user message sender deviceId:{} deviceSession:{} identifier:{} credit:{} time:{} datalen:{} data: {} ".format(senderDeviceId,sessionId,identifier,credit,time , len(data),self.__toHexString(data)))
        if self.__userMessageListener is not None:
            if self.__userMessageListener.paramCount == 2:
                self.__userMessageListener.toCall(senderDeviceId,data)
            else:
                self.__userMessageListener.toCall(senderDeviceId,data,sessionId,identifier,credit,time)

        else:
            self.__logger.warning("got user message but no function to process was set")

    def __onSyncMessage(self,senderDeviceId,messageId, data,sessionId=None,identifier=None,credit=None,time=None):
        self.__logger.debug("got user sync sender senderDeviceId:{} deviceSession:{} identifier:{} credit:{} time:{} messageId:{} datalen:{} data: {} ".format(senderDeviceId,sessionId,identifier,credit,time, messageId, len(data),self.__toHexString(data)))
        response=None

        if self.__userSyncMessageListener is not None:
            if self.__userMessageListener.paramCount == 2:
                response = self.__userSyncMessageListener.toCall(senderDeviceId, data)
            else:
                response = self.__userSyncMessageListener.toCall(senderDeviceId, data, sessionId,identifier, credit, time)

            if response is None:
                response=[]

            self.send(remotemeMessages.getSyncResponseMessage(messageId,response))
        else:
            self.__logger.warning("got user sync message but no function to process was set")


    def __onDeviceConnectionChange(self,data,size):
        reader = RemoteMeDataReader(data)
        size = int(size/3)
        self.__logger.warning("size:{}".format(size))

        for i in range(0,size):
            deviceId = reader.readUInt16()
            state = reader.readUInt8() == 1
            for listener in self.__onDeviceConnectionChangeListeners:
                listener(deviceId,state)



    def __onConnectionChange(self,data):
        reader = RemoteMeDataReader(data)

        # data and type already took

        deviceId = reader.readUInt16()
        type = reader.readUInt8()#  type 1 = weboscket type 2 = webrtc
        state = remotemeStruct.ConnectionState(reader.readUInt8())

        if type == 1:
            for toCall in self.__onWebsocketConnectionChangeListeners:
                toCall(state)

        elif type == 2:
            for toCall in self.__onWebRtcConnectionChangeListeners:
                toCall(state)

    def  send(self,message):
        self.__socketObj.sendall(message)

    def sendRest(self, message):
        self.__socketObj.sendall(message)

    def __exit__(self, exc_type, exc_value, traceback):
        self.__logger.debug("Exit remoteme python with id {}".format(self.__ownId))
        if self.__socketObj is not None:
            self.__socketObj.close()
            self.__socketObj = None

        if self.__threadRead is not None:
            self.__threadRead.join(1000)


    def startRemoteMe(self,sysargv):
        if (len(sysargv)>=5):
            parentId = int(sysargv[2])
            ownId = int(sysargv[3])
            port = int(sysargv[4])
            name="python script"
            if len(sysargv)==6:
                name=sysargv[5]

            self.startRemoteMeDirect(port,parentId,ownId,name)

        else:
            self.__logger.debug("usable working dir parentId ownId port deviceName")
            self.__logger.debug("got parameters {} : {}".format(len(sysargv), sysargv))
            exit(1)

    def getDeviceId(self):
        return self.__ownId

    def startRemoteMeDirect(self, port, parentId, ownId,name):
        if self.__socketObj is not None:
            self.__logger.warning("Remote Me already started")
            return


        self.__logger.debug("starting remogemeMe port:{} parentId:{} ownId:{} name:{}".format(port, parentId, ownId,name))
        self.__ownId = ownId

        self.__socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socketObj.connect(("localhost", port))

        self.__threadRead = threading.Thread(target=self.__readFromSocket)
        self.__threadRead.daemon = True
        self.__threadRead.start()

        self.send(remotemeMessages.getRegisterLeafDeviceMessage(parentId, self.__ownId, name,
                                                                  remotemeStruct.LeafDeviceType.LD_EXTERNAL_SCRIPT))
        self.__logger.debug("deivice has been regieteres at parent id:{} name:{} ".format(self.__ownId,name))

    def setUserMessageListener(self, function):
        self.__userMessageListener= FunctionCaller(function)

    def setUserSyncMessageListener(self, function):
        self.__userSyncMessageListener= FunctionCaller(function)

    def addWebRtcConnectionChangeListener(self, function):
        self.__onWebRtcConnectionChangeListeners.append(function)

    def addWebsocketConnectionChangeListener(self, function):
        self.__onWebsocketConnectionChangeListeners.append(function)

    def sendUserMessage(self,receiveDeviceId,data):
        self.send(remotemeMessages.getUserMessage(remotemeStruct.UserMessageSettings.NO_RENEWAL, receiveDeviceId, self.__ownId, 0, data))

    def sendUserMessageRest(self, receiveDeviceId, data):
        self.sendRest(remotemeMessages.getUserMessage(remotemeStruct.UserMessageSettings.NO_RENEWAL, receiveDeviceId,  self.__ownId, 0, data))

    def logServerInfo(self, message):
        self.send(remotemeMessages.getLogMessage(remotemeStruct.LogLevel.INFO, message))

    def logServerWarn(self, message):
        self.send(remotemeMessages.getLogMessage(remotemeStruct.LogLevel.WARN, message))

    def logServerError(self, message):
        self.send(remotemeMessages.getLogMessage(remotemeStruct.LogLevel.ERROR, message))

    def sendPushNotificationMessage(self, webPageDeviceId,title,body,badge,icon,image,vibrate=None):
        self.send(remotemeMessages.getPushNotificationMessage(webPageDeviceId,title,body,badge,icon,image,vibrate))

    def sendDecreaseGuestKeyCreditAndTimeMessage(self, sessionId, credit,time):
        self.send(remotemeMessages.getDecreaseGuestKeyCreditAndTimeMessage(self.__ownId, sessionId,credit, time))


    def subscribeDeviceConnectionChangeEvent(self,listener):
        self.subscribeEvent(remotemeStruct.EventSubscriberType.DEVICE_CONNECTION,listener)

    def subscribeEvent(self, type, listener):
        self.__onDeviceConnectionChangeListeners.append(listener)
        self.send(remotemeMessages.getSubscribeMessage([type]))

    def wait(self):
        self.__threadRead.join()

