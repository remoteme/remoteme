import time

import remotemeStruct
import logging


import remotemeMessages

from remoteMeDataReader import RemoteMeDataReader
from remoteMeDataWriter import RemoteMeDataWriter

class Variables:
    __observables = {}
    __remoteMe=None

    def __init__(self,remoteMe):
        self.__remoteMe=remoteMe

        self.__logger = logging.getLogger('Variables')
        self.__logger.info('creating an instance of Variables')



    def _RemoteMe__onVariableChangePropagate(self,data):
        reader = RemoteMeDataReader(data)

        # data and type already took


        senderDeviceId = reader.readInt16()
        receiverDeviceId = reader.readInt16()

        count = reader.readInt16()

        while count != 0:
            count = count-1

            type = remotemeStruct.VariableType(reader.readInt16())
            name = reader.readString()

            self.__logger.info("type:{} name:{} is bool {}".format(type, name,(type ==remotemeStruct.VariableType.BOOLEAN) ))

            if type ==remotemeStruct.VariableType.BOOLEAN:
                value = reader.readInt8()==1
                self.__logger.info("try to call {} {}".format(name,value))
                toCall= self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value)
                else:
                    self.__logger.info("ddint found caller")

            elif type ==remotemeStruct.VariableType.INTEGER:
                value = reader.readInt32()
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value)

            elif type == remotemeStruct.VariableType.TEXT:
                value = reader.readString()
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value)

            elif type == remotemeStruct.VariableType.SMALL_INTEGER_3:
                value = reader.readInt16()
                value2 = reader.readInt16()
                value3 = reader.readInt16()
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value,value2,value3)


            elif type == remotemeStruct.VariableType.SMALL_INTEGER_2:
                value = reader.readInt16()
                value2 = reader.readInt16()

                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value,value2)

            elif type == remotemeStruct.VariableType.INTEGER_BOOLEAN:
                value = reader.readInt32()
                value2 =reader.readInt8()==1
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value,value2)

            elif type == remotemeStruct.VariableType.DOUBLE:
                value = reader.readDouble()
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value)

            elif type == remotemeStruct.VariableType.TEXT_2:
                value = reader.readString()
                value2 = reader.readString()
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value,value2)
            elif type == remotemeStruct.VariableType.SMALL_INTEGER_2_TEXT_2:
                value = reader.readInt16()
                value2 = reader.readInt16()
                value3 = reader.readString()
                value4 = reader.readString()
                toCall = self.__observables.get(name + str(type.value),None)
                if toCall != None:
                    toCall(value, value2,value3,value4)

    def setBoolean(self,name,value,ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.BOOLEAN._value_)
        writer.writeString(name)
        writer.writeUInt8(1 if value else 0)
        self.__remoteMe.send(remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(),ignoreCurrent,writer.getBytes()))

    def setInteger(self,name,value,ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.INTEGER._value_)
        writer.writeString(name)
        writer.writeInt32(value)
        self.__remoteMe.send(remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setText(self,name, value, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.TEXT._value_)
        writer.writeString(name)
        writer.writeString(value)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setSmallInteger3(self,name, value, value2, value3, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.SMALL_INTEGER_3._value_)
        writer.writeString(name)
        writer.writeInt16(value)
        writer.writeInt16(value2)
        writer.writeInt16(value3)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setSmallInteger2(self,name, value, value2, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.SMALL_INTEGER_2._value_)
        writer.writeString(name)
        writer.writeInt16(value)
        writer.writeInt16(value2)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setIntegerBoolean(self,name, value, value2, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.INTEGER_BOOLEAN._value_)
        writer.writeString(name)
        writer.writeInt32(value)
        writer.writeUInt8(1 if value2 else 0)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setDouble(self,name, value, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.DOUBLE._value_)
        writer.writeString(name)
        writer.writeDouble(1 if value else 0)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setText2(self, name, value, value2, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.TEXT_2._value_)
        writer.writeString(name)
        writer.writeString(value)
        writer.writeString(value2)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def setSmallInteger2Text2(self, name, value, value2,value3,value4, ignoreCurrent=False):
        writer = RemoteMeDataWriter()
        writer.writeUInt16(remotemeStruct.VariableType.SMALL_INTEGER_2_TEXT_2._value_)
        writer.writeString(name)
        writer.writeInt16(value)
        writer.writeInt16(value2)
        writer.writeString(value3)
        writer.writeString(value4)
        self.__remoteMe.send(
            remotemeMessages.getVariableChangeMessage(self.__remoteMe.getDeviceId(), ignoreCurrent, writer.getBytes()))

    def observeBoolean(self,name, onChange):
        self.__observe(name, remotemeStruct.VariableType.BOOLEAN, onChange)

    def observeInteger(self,name, onChange):
        self.__observe(name, remotemeStruct.VariableType.INTEGER, onChange)

    def observeText(self, name,onChange):
        self.__observe(name, remotemeStruct.VariableType.TEXT, onChange)

    def observeSmallInteger3(self, name, onChange):
        self.__observe(name, remotemeStruct.VariableType.SMALL_INTEGER_3, onChange)

    def observeSmallInteger2(self, name, onChange):
        self.__observe(name, remotemeStruct.VariableType.SMALL_INTEGER_2, onChange)

    def observeIntegerBoolean(self, name, onChange):
        self.__observe(name, remotemeStruct.VariableType.INTEGER_BOOLEAN, onChange)

    def observeDouble(self, name, onChange):
        self.__observe(name, remotemeStruct.VariableType.DOUBLE, onChange)


    def observeText2(self, name, onChange):
        self.__observe(name, remotemeStruct.VariableType.TEXT_2, onChange)

    def observeSmallInteger2Text2(self, name, onChange):
        self.__observe(name, remotemeStruct.VariableType.SMALL_INTEGER_2_TEXT_2, onChange)

    def __observe(self, name, type, onChange):
        size = 2 + 2 + 2 + len(name) + 1

        wr = RemoteMeDataWriter()
        wr.writeInt16(remotemeStruct.MessageType.OBSERVER_REGISTER_MESSAGE.value)
        wr.writeInt16(size)
        wr.writeInt16(self.__remoteMe.getDeviceId())
        wr.writeInt16(1)
        wr.writeInt16(type.value)
        wr.writeString(name)

        self.__logger.info("sending variable {} type:{}".format(name,type))
        self.__remoteMe.send(wr.getBytes())

        self.__observables[name+str(type.value)]=onChange

    def __sendNow(self,name,type):
        size = 2 + 2 + 2 + len(name) + 1

        wr = RemoteMeDataWriter()

        wr.writeInt16(remotemeStruct.MessageType.OBSERVER_REGISTER_MESSAGE.value)
        wr.writeInt16(size)
        wr.writeInt16(self.__remoteMe.getDeviceId())
        wr.writeInt16(1)
        wr.writeInt16(type.value)
        wr.writeString(name)

        self.__logger.info("sending variable {} type:{}".format(name, type))
        self.__remoteMe.send(wr.getBytes())

        self.__observables[name + str(type.value)] = onChange