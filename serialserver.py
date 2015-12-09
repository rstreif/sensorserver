"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Server for serial sensors.
"""

import os, threading, serial, time


# Serial Server
class SerialServer(threading.Thread):
    """
    Server that continuously sends messages to a serial port and tries
    to read them back to check if the sensor is activated. Sensor activated
    means that RX and TX lines are bridged.
    """
    
    sensor = None
    logger = None
    callback = None
    loop = True
    
    def __init__(self, sensor, logger = None, callback = None):
        self.sensor = sensor
        self.logger = logger
        self.callback = callback
        threading.Thread.__init__(self)

    def run(self):
        if self.logger: self.logger.info('Sensor %s starting', self.sensor['name'])
        debounce = 0
        status = False
        match = False
        ser = None
        while self.loop == True:
            try:
                ser = serial.Serial(self.sensor['port'], self.sensor['baud'], timeout = self.sensor['timeout'])
                while self.loop == True:
                    ser.write(self.sensor['message'])
                    match = (ser.read(len(self.sensor['message'])) == self.sensor['message'])
                    if not status and match:
                        time.sleep(self.sensor['timeout'])
                        debounce += 1
                    elif status and not match:
                        debounce += 1
                    else:
                        debounce = 0
                    if debounce >= self.sensor['debounce'] -1:
                        debounce = 0
                        status = not status
                        if self.logger: self.logger.info('Sensor %s: changed: %s', self.sensor['name'], status)
                        if self.callback: self.callback(self.sensor['name'], status)
            except Exception as e:
                if self.logger: self.logger.error('Server %s: Exception: %s', self.sensor['name'], e)
                debounce = 0
                status = False
                if ser: ser.close()
                time.sleep(self.sensor['timeout'])
        
    def shutdown(self):
        self.loop = False
