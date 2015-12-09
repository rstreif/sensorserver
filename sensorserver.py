"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
"""

"""
Sensorserver: Parallel I/O via Serial Ports.
"""

import sys, os, logging, jsonrpclib
import time, socket, urlparse, datetime
from signal import *


import __init__, settings
from daemon import Daemon

import serialserver

logger = logging.getLogger('sensor.default')

class SensorServer(Daemon):
    """
    Main server daemon
    """
    rvi_service_edge = None
    servers = {}
    
    
    def shutdown(self, *args):
        """
        Clean up and exit.
        """
        logger.info('Sensor Server: Caught signal: %d. Shutting down...', args[0])
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """
        Clean up.
        """
        for key, value in self.servers.iteritems():
            if value is not None:
                value.shutdown()

    def startup(self):
        """
        Initialization and startup
        """
        logger.info('Sensor Server: Starting...')

        logger.debug('Sensor Server: General Configuration: ' + 
            'RVI_SERVICE_EDGE_URL: '  + settings.RVI_SERVICE_EDGE_URL +
            'RVI_SERVICE_SEND_TIMEOUT: '  + str(settings.RVI_SEND_TIMEOUT)
        )

        # setup RVI Service Edge
        logger.info('Sensor Server: Setting up outbound connection to RVI Service Edge at %s', settings.RVI_SERVICE_EDGE_URL)
        self.rvi_service_edge = jsonrpclib.Server(settings.RVI_SERVICE_EDGE_URL)
        
        # Startup for individual sensors
        logger.info('Sensor Server: Starting sensors...')
        for sensor in settings.SENSOR_CONFIG:
            if sensor['enable'] == True:
                logger.info('Starting sensor %s...', sensor['name'])
                server = serialserver.SerialServer(sensor, logger, callback)
                server.start()
                self.servers[sensor['name']] = server
                logger.info('Running.')
            else:
                logger.info('Sensor %s disabled.', sensor['name'])
                
        return True

    def run(self):
        """
        Main execution loop
        """
        # catch signals for proper shutdown
        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.shutdown)
        # start servers
        self.startup()
        # main loop
        logger.info('Sensor Server: Entering Main Loop')
        while True:
            try:
                if settings.HEARTBEAT_ENABLE == True:
                    logger.info('Sensor Server Heartbeat')
                time.sleep(settings.MAIN_LOOP_INTERVAL)
            except KeyboardInterrupt:
                print ('\n')
                break

def callback(caller, status):
    logger.info('Callback from sensor %s, status: %s', caller, status)
    if caller == 'seat':
        if status == True:
            message = '{ "command": "driver_seat_changed", "occupied": "1" }'
            sendIVI(message)
            message = '[{ "channel": "seats", "value": { "frontleft": "occupied" } }]'
            sendRVI(message)
        else:
            message = '{ "command": "driver_seat_changed", "occupied": "0" }'
            sendIVI(message)
            message = '[{ "channel": "seats", "value": { "frontleft": "vacant" } }]'
            sendRVI(message)
            
    elif caller == 'trunk':
        if status == True:
            message = '[{ "channel": "trunk", "value": "open" }]'
            sendRVI(message)
        else:
            message = '[{ "channel": "trunk", "value": "closed" }]'
            sendRVI(message)

    else:
        pass
    
def sendIVI(message):
    logger.info('Sending to IVI: %s, message: %s', settings.IVI_SERVICE_EDGE_URL, message)
    try:
        url = urlparse.urlparse(settings.IVI_SERVICE_EDGE_URL)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((url.hostname, url.port))
        sock.send(message)
        sock.close()
    except Exception as e:
        logger.error('Sending to IVI failed: %s', e)
            

def sendRVI(message):
    logger.info('Sending to RVI: %s, message: %s', settings.RVI_SERVICE_EDGE_URL, message)
    try:
        server = jsonrpclib.Server(settings.RVI_SERVICE_EDGE_URL)
        server.message(service_name = settings.RVI_SERVICE_ID,
                       timeout = int(time.time()) + settings.RVI_SEND_TIMEOUT,
                       parameters = [
                           {"vin": settings.RVI_VIN},
                           {"timestamp": datetime.datetime.now().isoformat()},
                           {"data": message}
                       ]
                      )
    except Exception as e:
        logger.error('Sending to RVI failed: %s', e)
                    


def usage():
    """
    Print usage message
    """
    print "Sensor Server: Usage: %s foreground|start|stop|restart" % sys.argv[0]        
    
"""
Main Function
"""    
if __name__ == "__main__":
    pid_file = '/var/run/' + os.path.splitext(__file__)[0] + '.pid'
    sensor_server = None
    if len(sys.argv) == 3:
        pid_file = sys.argv[2]
    sensor_server = SensorServer(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
    if len(sys.argv) >= 2:
        if sys.argv[1] in ('foreground', 'fg'):
            # in foreground we also log to the console
            logger = logging.getLogger('sensor.console')
            sensor_server.run()
        elif sys.argv[1] in ('start', 'st'):
            sensor_server.start()
        elif sys.argv[1] in ('stop', 'sp'):
            sensor_server.stop()
        elif sys.argv[1] in ('restart', 're'):
            sensor_server.restart()
        else:
            print "Sensor Server: Unknown command."
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)
