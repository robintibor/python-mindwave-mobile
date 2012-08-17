# This test tries to verify that the neurosky headset sends packets 
# according to the specification at http://wearcam.org/ece516/mindset_communications_protocol.pdf :)
# You can run this to check whether the neurosky headset behaves as described in this specification
import bluetooth
import unittest

mindwaveMobileSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
mindwaveMobileAddress = '9C:B7:0D:72:CD:02'
numberOfPacketsToTest = 300;

def setUpModule():
    connectToMindwaveHeadset()

def tearDownModule():
    closeConnectionToMindwaveHeadset();

def connectToMindwaveHeadset():
    try:
        mindwaveMobileSocket.connect((mindwaveMobileAddress, 1))
        return;
    except bluetooth.btcommon.BluetoothError as error:
        print "Could not connect: ", error

def closeConnectionToMindwaveHeadset():
    mindwaveMobileSocket.close();

class ProtocolTest(unittest.TestCase):
    def testIncomingBytes(self):
        numberOfTestedPackets = 0;
        while(numberOfTestedPackets < numberOfPacketsToTest):
            self._goToStartOfPacket();
            payloadBytes, checkSum = self._readOnePacket();
            self._checkPacket(payloadBytes, checkSum);
            numberOfTestedPackets += 1

    def _goToStartOfPacket(self):
        # Need to read TWO sync bytes, then you are at the start of a packet
        syncByteCode = 0xaa
        maximumBytesBeforePacketSync = 200  # to prevent this test from running forever
        bytesRead = 0
        while(bytesRead < maximumBytesBeforePacketSync):
            receivedByte = self._getByteFromMindwaveHeadset();
            bytesRead += 1
            if (receivedByte == syncByteCode):                
                receivedByte = self._getByteFromMindwaveHeadset();
                bytesRead += 1
                if (receivedByte == syncByteCode):
                    return
        self.fail("should find packet sync bytes before 200 bytes are read...")

    def _getByteFromMindwaveHeadset(self):
        return  ord(mindwaveMobileSocket.recv(1))
    
    def _readOnePacket(self):
        payloadLength = self._readPayloadLength();
        payloadBytes, checkSum = self._readPacket(payloadLength);
        return payloadBytes, checkSum
    
    def _readPayloadLength(self):
        payloadLength = self._getByteFromMindwaveHeadset()
        self.assertLess(payloadLength, 170, "payloadLength should be smaller than 170")
        return payloadLength
    
    def _readPacket(self, payloadLength):
        payloadBytes = self._getBytesFromMindwaveHeadset(payloadLength)
        checkSum = self._getByteFromMindwaveHeadset()
        return payloadBytes, checkSum
        
    def _getBytesFromMindwaveHeadset(self, numberOfBytes):
        receivedChars  = ""
        while (len(receivedChars) < numberOfBytes):
            receivedChars += mindwaveMobileSocket.recv(numberOfBytes - len(receivedChars))
        assert len(receivedChars) == numberOfBytes
        return map(ord, receivedChars);
    
    def _checkPacket(self, payloadBytes, checkSum):
        self._checkCheckSum(payloadBytes, checkSum)
        self._checkPayloadOfPacket(payloadBytes)
    
    def _checkCheckSum(self, payloadBytes, checkSum):
        sumOfPayload = sum(payloadBytes)
        lastEightBits = sumOfPayload % 256
        invertedLastEightBits = self._computeOnesComplement(lastEightBits) #1's complement!
        self.assertEqual(invertedLastEightBits, checkSum, "checksum should match inverted last 8 bits of sum of the payload")
    
    def _computeOnesComplement(self, lastEightBits):
        return ~lastEightBits + 256

    def _checkPayloadOfPacket(self, payloadBytes):
        remainingPayloadBytes = payloadBytes
        while (len(remainingPayloadBytes) > 0):
            dataRowCode, dataValueBytes, remainingPayloadBytes = self._extractDataRow(remainingPayloadBytes)
            self._checkDataRow(dataRowCode, dataValueBytes)
    
    def _extractDataRow(self, payloadBytes):
        dataRowCode, dataValueLength, remainingPayloadBytes = self._extractFirstDataType(payloadBytes)
        dataBytes = remainingPayloadBytes[0:dataValueLength]
        remainingPayloadAfterDataRow = remainingPayloadBytes[dataValueLength:]
        return dataRowCode, dataBytes, remainingPayloadAfterDataRow
    
    def _extractFirstDataType(self, payloadBytes):
        numberOfExtendedCodeBytes = self._extractNumberOfExtendedCodeBytes(payloadBytes)
        dataRowCode = payloadBytes[numberOfExtendedCodeBytes]
        if (dataRowCode > 0x7f):
            dataValueLength = payloadBytes[numberOfExtendedCodeBytes + 1];
            # remaining payload starts at the beginning of the data value
            # after extended code bytes and row code and length byte!
            remainingPayloadBytes = payloadBytes[(numberOfExtendedCodeBytes + 2):]
        else:
            dataValueLength = 1;
            remainingPayloadBytes = payloadBytes[(numberOfExtendedCodeBytes + 1):]
        return dataRowCode, dataValueLength, remainingPayloadBytes
        
    def _extractNumberOfExtendedCodeBytes(self, payloadBytes):
        numberOfExtendedCodeBytes = 0
        for byte in payloadBytes:
            if byte == 0x55:
                numberOfExtendedCodeBytes += 1
            else:
                break;
        return numberOfExtendedCodeBytes;
    
    def _checkDataRow(self, dataRowCode, dataValueBytes):
        if (dataRowCode == 0x02):
            self.assertEqual(len(dataValueBytes), 1, "poor signal values should have one byte")
        elif (dataRowCode == 0x04):
            self.assertEqual(len(dataValueBytes), 1, "attention signal values should have one byte")
            self.assertLess(dataValueBytes[0], 101, "attention value should be inbetween 0 and 100")
        elif (dataRowCode == 0x05):
            self.assertEqual(len(dataValueBytes), 1, "meditation signal values should have one byte")
            self.assertLess(dataValueBytes[0], 101, "meditation value should be inbetween 0 and 100")
        elif (dataRowCode == 0x16):
            self.assertEqual(len(dataValueBytes), 1, "blink strength signal values should have one byte")
        elif (dataRowCode == 0x80):
            self.assertEqual(len(dataValueBytes), 2, "raw values should have two bytes")
        elif (dataRowCode == 0x83):
            self.assertEqual(len(dataValueBytes), 24, "eeg power values should have 24 bytes")
        else:
            self.fail("unknown data row code " + str(dataRowCode));
        
if __name__ == '__main__':
    unittest.main()