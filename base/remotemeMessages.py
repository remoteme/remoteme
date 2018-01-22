import struct

import remotemeStruct
import array

def getUserMessage(userMessageSettings,receiverDeviceId,senderDeviceId,messageId,data):
    size = 7 + len(data)
    return struct.pack(">hhBhhh{0}s".format(len(data)), remotemeStruct.MessageType.USER_MESSAGE._value_, size, userMessageSettings._value_, receiverDeviceId,
                               senderDeviceId, messageId, data)


def getWebRtcMessage(data):
    return struct.pack(">hh{0}s".format(len(data)), remotemeStruct.MessageType.USER_MESSAGE._value_, len(data), data)


def getLogMessage(logLevel,message):
    byteArray = message.encode("utf-8")
    size = 1 + len(byteArray)+1
    return struct.pack(">hhB{0}sB".format(len(byteArray)), remotemeStruct.MessageType.LOG._value_, size, logLevel._value_, byteArray, 0)

def getSyncResponseMessage(messageId,byteArray):
    byteArray=bytearray( byteArray)
    size = 8 + len(byteArray)
    return struct.pack(">hhQ{0}s".format(len(byteArray)), remotemeStruct.MessageType.SYNC_MESSAGE_RESPONSE._value_, size, messageId, byteArray)

def getRegisterLeafDeviceMessage(parentId,deviceId,deviceName,leafDeviceType):
    byteArray = deviceName.encode("utf-8")

    size = 4 + len(byteArray)+1+2
    return struct.pack(">hhhh{0}sBh".format(len(byteArray)), remotemeStruct.MessageType.REGISTER_CHILD_DEVICE._value_, size, parentId, deviceId, byteArray, 0, leafDeviceType)

def writeAddDataMessage(time,addDataMessageSetting,dataSeries):
    size = 8+1 + len(dataSeries)*10
    dataSeriesArray=[]

    for x in dataSeries:
        for b in struct.pack(">hd", x.seriesId, x.value):
            dataSeriesArray.append(b)

    dataSeriesArray=bytearray(dataSeriesArray)

    return 0

