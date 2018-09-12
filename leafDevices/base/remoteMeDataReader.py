import socket
import threading

import struct

import remotemeMessages
import remotemeStruct
import logging

from remotemeMessages import getUserMessage


class RemoteMeDataReader:

    def __init__(self, data):
        self.__logger = logging.getLogger('remoteMe.RemoteMeData')
        if isinstance(data, str):
            self.data = data.encode("utf-8")
        else:
            self.data = data

        self.offset = 0

    def readInt8(self):
        [ret] = struct.unpack_from(">b", self.data, self.offset)
        self.offset += struct.calcsize(">b")
        return ret

    def readString(self):
        dataRet = []

        ret = self.readUInt8()
        while ret != 0:
            dataRet.append(ret)
            ret = self.readUInt8()

        return struct.pack("B" * len(dataRet), *dataRet).decode('utf8')

    def readData(self, size):
        dataRet = []

        while size != 0:
            dataRet.append(self.readUInt8())
            size = size - 1

        return dataRet

    def readUInt8(self):
        [ret] = struct.unpack_from(">B", self.data, self.offset)
        self.offset += struct.calcsize(">B")
        return ret

    def readInt16(self):
        [ret] = struct.unpack_from(">h", self.data, self.offset)
        self.offset += struct.calcsize(">h")
        return ret

    def readUInt16(self):
        [ret] = struct.unpack_from(">H", self.data, self.offset)
        self.offset += struct.calcsize(">H")
        return ret

    def readInt32(self):
        [ret] = struct.unpack_from(">i", self.data, self.offset)
        self.offset += struct.calcsize(">i")
        return ret

    def readUInt32(self):
        [ret] = struct.unpack_from(">I", self.data, self.offset)
        self.offset += struct.calcsize(">I")
        return ret

    def readDouble(self):
        [ret] = struct.unpack_from(">d", self.data, self.offset)
        self.offset += struct.calcsize(">d")
        return ret