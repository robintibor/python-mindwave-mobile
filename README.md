Some scripts to access the data streamed by the **Neurosky Mindwave Mobile** Headset over Bluetooth on Linux.

Usage in python:

'mindwaveDataPointReader = MindwaveDataPointReader()'
mindwaveDataPointReader.start() # connects to the mindwave mobile headset...
dataPoint = mindwaveDataPointReader.readNextDataPoint() # reads one data point, data point types are specified in  MindwaveDataPoints.py'