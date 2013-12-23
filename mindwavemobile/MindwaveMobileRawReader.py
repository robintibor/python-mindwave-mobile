import bluetooth
import time


class MindwaveMobileRawReader:
    START_OF_PACKET_BYTE = 0xaa;
    def __init__(self):
        self._buffer = [];
        self._bufferPosition = 0;
        
    def connectToMindWaveMobile(self):
        # connecting via bluetooth RFCOMM
        self.mindwaveMobileSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        mindwaveMobileAddress = '9C:B7:0D:72:CD:02';
        while(True):
            try:
                self.mindwaveMobileSocket.connect((mindwaveMobileAddress, 1))
                return;
            except bluetooth.btcommon.BluetoothError as error:
                print "Could not connect: ", error, "; Retrying in 5s..."
                time.sleep(5) 
    
    def _readMoreBytesIntoBuffer(self, amountOfBytes):
        newBytes = self._readBytesFromMindwaveMobile(amountOfBytes)
        self._buffer += newBytes
    
    def _readBytesFromMindwaveMobile(self, amountOfBytes):
        missingBytes = amountOfBytes
        receivedBytes = ""
        # Sometimes the socket will not send all the requested bytes
        # on the first request, therefore a loop is necessary...
        while(missingBytes > 0):
            receivedBytes += self.mindwaveMobileSocket.recv(missingBytes)
            missingBytes = amountOfBytes - len(receivedBytes)
        return receivedBytes;

    def peekByte(self):
        self._ensureMoreBytesCanBeRead();
        return ord(self._buffer[self._bufferPosition])

    def getByte(self):
        self._ensureMoreBytesCanBeRead(100);
        return self._getNextByte();
    
    def  _ensureMoreBytesCanBeRead(self, amountOfBytes):
        if (self._bufferSize() <= self._bufferPosition + amountOfBytes):
            self._readMoreBytesIntoBuffer(amountOfBytes)
    
    def _getNextByte(self):
        nextByte = ord(self._buffer[self._bufferPosition]);
        self._bufferPosition += 1;
        return nextByte;

    def getBytes(self, amountOfBytes):
        self._ensureMoreBytesCanBeRead(amountOfBytes);
        return self._getNextBytes(amountOfBytes);
    
    def _getNextBytes(self, amountOfBytes):
        nextBytes = map(ord, self._buffer[self._bufferPosition: self._bufferPosition + amountOfBytes])
        self._bufferPosition += amountOfBytes
        return nextBytes
    
    def clearAlreadyReadBuffer(self):
        self._buffer = self._buffer[self._bufferPosition : ]
        self._bufferPosition = 0;
    
    def _bufferSize(self):
        return len(self._buffer);
    
#------------------------------------------------------------------------------ 