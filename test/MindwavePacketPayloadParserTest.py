import unittest
from MindwavePacketPayloadParser import MindwavePacketPayloadParser
from MindwaveDataPoints import RawDataPoint, PoorSignalLevelDataPoint,\
    MeditationDataPoint, AttentionDataPoint, EEGPowersDataPoint, BlinkDataPoint



class ParseRawValueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = [0x80, 0x02, 0x60, 0x0] # first raw value
        payload.extend([0x80, 0x02, 0x13, 0x12]) # second raw value
        payload.extend([0x2, 0x55]) # poor signal level value
        payload.extend([0x4, 0x25]) # attention level value
        payload.extend([0x5, 0x35]) # meditation level value
        payload.extend([0x16, 0x15]) # blink level value
        payload.extend([0x83, 0x18, 0x15, 0x13, 0x17, 0x12, 0x11, 0x10, 0x9, 0x8, 0x7]) # 3 eeg powers
        payload.extend([0x14, 0x13, 0x17, 0x12, 0x11, 0x10, 0x9, 0x8, 0x5]) # 3 more eeg powers
        payload.extend([0xaf, 0x13, 0xbf, 0x0, 0x1, 0x0]) # 2 more eeg powers
        cls._payloadParser = MindwavePacketPayloadParser(payload)
        cls._dataPoints = cls._payloadParser.parseDataPoints()
    
    def testReadingRawValueCorrectly(self):
        dataPoint = self._dataPoints[0]
        self.readingValueCorrectly(dataPoint.__class__, dataPoint.rawValue, \
                                  RawDataPoint, (0x60 << 8) | 0x0,\
                                  "should parse correct first raw value")
    
    def testReadingSecondRawValueCorrectly(self):
        dataPoint = self._dataPoints[1]        
        self.readingValueCorrectly(dataPoint.__class__, dataPoint.rawValue, \
                                  RawDataPoint, (0x13 << 8) | 0x12,\
                                  "should parse correct second raw value")
    
    def testReadingPoorSignalLevelCorrectly(self):
        dataPoint = self._dataPoints[2];
        self.readingValueCorrectly(dataPoint.__class__, dataPoint.amountOfNoise, \
                                  PoorSignalLevelDataPoint, 0x55,\
                                  "should parse correct noise level")
    
    def testReadingAttentionLevelCorrectly(self):
        dataPoint = self._dataPoints[3];
        self.readingValueCorrectly(dataPoint.__class__, dataPoint.attentionValue, \
                                  AttentionDataPoint, 0x25,\
                                  "should parse correct attention level")
    
    def testReadingMeditationLevelCorrectly(self):
        dataPoint = self._dataPoints[4];
        self.readingValueCorrectly(dataPoint.__class__, dataPoint.meditationValue, \
                                  MeditationDataPoint, 0x35,\
                                  "should parse correct meditation level")
    
    def testReadingBlinkLevelCorrectly(self):
        dataPoint = self._dataPoints[5];
        self.readingValueCorrectly(dataPoint.__class__, dataPoint.blinkValue, \
                                  BlinkDataPoint, 0x15,\
                                  "should parse correct blink level")
        
    def readingValueCorrectly(self, actualClass, actualValue, expectedClass, expectedValue, msg):
        self.assertTrue(actualClass is expectedClass, msg)
        self.assertEqual(actualValue, expectedValue, msg)
    
    def testReadingEEGLevelsCorrectly(self):
        dataPoint = self._dataPoints[6];
        self.assertIs(dataPoint.__class__, EEGPowersDataPoint, "eeg powers should be parsed correctly")
        self.assertEqual(dataPoint.delta, (0x15 << 16) | (0x13 << 8) | 0x17, "delta should be parsed correctly")
        self.assertEqual(dataPoint.theta, (0x12 << 16) | (0x11 << 8) | 0x10, "theta should be parsed correctly")
        self.assertEqual(dataPoint.lowAlpha, (0x9 << 16) | (0x8 << 8) | 0x7, "lowAlpha should be parsed correctly")
        self.assertEqual(dataPoint.highAlpha, (0x14 << 16) | (0x13 << 8) | 0x17, "highAlpha should be parsed correctly")
        self.assertEqual(dataPoint.lowBeta, (0x12 << 16) | (0x11 << 8) | 0x10, "lowBeta should be parsed correctly")
        self.assertEqual(dataPoint.highBeta, (0x9 << 16) | (0x8 << 8) | 0x5, "highBeta should be parsed correctly")
        self.assertEqual(dataPoint.lowGamma, (0xaf << 16) | (0x13 << 8) | 0xbf, "lowGamma should be parsed correctly")
        self.assertEqual(dataPoint.midGamma, (0x0 << 16) | (0x1 << 8) | 0x0, "midGamma should be parsed correctly")
        
        
if __name__ == '__main__':
    unittest.main()