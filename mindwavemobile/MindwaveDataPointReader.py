from MindwaveMobileRawReader import MindwaveMobileRawReader
import struct
import collections

from MindwavePacketPayloadParser import MindwavePacketPayloadParser

class MindwaveDataPointReader:
    def __init__(self):
        self._mindwaveMobileRawReader = MindwaveMobileRawReader()
        self._dataPointQueue = collections.deque()

    def start(self):
        self._mindwaveMobileRawReader.connectToMindWaveMobile()
        
    def readNextDataPoint(self):
        if (not self._moreDataPointsInQueue()):
            self._putNextDataPointsInQueue()
        return self._getDataPointFromQueue()

    def _moreDataPointsInQueue(self):
        return len(self._dataPointQueue) > 0
    
    def _getDataPointFromQueue(self):
        return self._dataPointQueue.pop();
    
    def _putNextDataPointsInQueue(self):
        dataPoints = self._readDataPointsFromOnePacket()
        self._dataPointQueue.extend(dataPoints)
    
    def _readDataPointsFromOnePacket(self):
        self._goToStartOfNextPacket()
        payloadBytes, checkSum = self._readOnePacket()
        if (not self._checkSumIsOk(payloadBytes, checkSum)):
            print "checksum of packet was not correct, discarding packet..."
            return self._readDataPointsFromOnePacket();
        else:
            dataPoints = self._readDataPointsFromPayload(payloadBytes)
        self._mindwaveMobileRawReader.clearAlreadyReadBuffer()
        return dataPoints;
        
    def _goToStartOfNextPacket(self):
        while(True):
            byte = self._mindwaveMobileRawReader.getByte()
            if (byte == MindwaveMobileRawReader.START_OF_PACKET_BYTE):  # need two of these bytes at the start..
                byte = self._mindwaveMobileRawReader.getByte()
                if (byte == MindwaveMobileRawReader.START_OF_PACKET_BYTE):
                    # now at the start of the packet..
                    return;

    def _readOnePacket(self):
            payloadLength = self._readPayloadLength();
            payloadBytes, checkSum = self._readPacket(payloadLength);
            return payloadBytes, checkSum
    
    def _readPayloadLength(self):
        payloadLength = self._mindwaveMobileRawReader.getByte()
        return payloadLength

    def _readPacket(self, payloadLength):
        payloadBytes = self._mindwaveMobileRawReader.getBytes(payloadLength)
        checkSum = self._mindwaveMobileRawReader.getByte()
        return payloadBytes, checkSum

    def _checkSumIsOk(self, payloadBytes, checkSum):
        sumOfPayload = sum(payloadBytes)
        lastEightBits = sumOfPayload % 256
        invertedLastEightBits = self._computeOnesComplement(lastEightBits) #1's complement!
        return invertedLastEightBits == checkSum;
    
    def _computeOnesComplement(self, lastEightBits):
        return ~lastEightBits + 256
        
    def _readDataPointsFromPayload(self, payloadBytes):
        payloadParser = MindwavePacketPayloadParser(payloadBytes)
        return payloadParser.parseDataPoints();
    
    
    
    