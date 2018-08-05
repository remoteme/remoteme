import time

import remotemeStruct
import logging

from remoteMeDataReader import RemoteMeDataReader
from remoteMeDataWriter import RemoteMeDataWriter



class Observers:
    __observables = {}
    __remoteMe=None

    def __init__(self,remoteMe):
        self.__remoteMe=remoteMe

        self.__logger = logging.getLogger('Observers')
        self.__logger.info('creating an instance of Observers')



    def _RemoteMe__onObserverChangePropagate(self,data):
        reader = RemoteMeDataReader(data)

        # data and type already took


        senderDeviceId = reader.readInt16()
        receiverDeviceId = reader.readInt16()

        count = reader.readInt16()

        while count != 0:
            count = count-1

            type = remotemeStruct.VariableOberverType(reader.readInt16())
            name = reader.readString()

            self.__logger.info("type:{} name:{} is bool {}".format(type, name,(type ==remotemeStruct.VariableOberverType.BOOLEAN) ))

            if type ==remotemeStruct.VariableOberverType.BOOLEAN:
                value = reader.readInt8()==1
                self.__logger.info("try to call {} {}".format(name,value))
                toCall= self.__observables[name + str(type.value)]
                if toCall != None:
                    toCall(value)
                else:
                    self.__logger.info("ddint found caller")

            elif type ==remotemeStruct.VariableOberverType.INTEGER:
                value = reader.readInt32()
                toCall = self.__observables[name + str(type.value)]
                if toCall != None:
                    toCall(value)





    def observeBoolean(self,name, onChange):
        self.observe(name, remotemeStruct.VariableOberverType.BOOLEAN, onChange)

    def observeInteger(self,name, onChange):
        self.observe(name, remotemeStruct.VariableOberverType.INTEGER, onChange)

    def observe(self,name, type, onChange):


        size = 2 + 2 + 2 + len(name) + 1

        wr = RemoteMeDataWriter()
        wr.writeInt16(remotemeStruct.MessageType.OBSERVER_REGISTER_MESSAGE.value)
        wr.writeInt16(size)
        wr.writeInt16(self.__remoteMe.getDeviceId())
        wr.writeInt16(1)
        wr.writeInt16(type.value)
        wr.writeString(name)

        self.__logger.info("sending observer {} type:{}".format(name,type))
        self.__remoteMe.send(wr.getBytes())

        self.__observables[name+str(type.value)]=onChange
