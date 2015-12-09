"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Settings for serial sensors
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)

# Logging settings
LOGGING_DIR = os.path.join(BASE_DIR, 'sensor.log')
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
             'level': 'DEBUG',
             'class': 'logging.StreamHandler',
             'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'sensor.default': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'sensor.console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# General Configuration
MAIN_LOOP_INTERVAL = 5
HEARTBEAT_ENABLE = False

# RVI Configuration
RVI_SERVICE_EDGE_URL = 'http://192.168.100.101:8801'
RVI_SEND_TIMEOUT = 10
RVI_SERVICE_ID = 'jlr.com/smarthome/myhome/vehicle/statusreport'
RVI_VIN = "L405"

# IVI Configuration
IVI_SERVICE_EDGE_URL = 'tcp://127.0.0.1:11264'
IVI_SEND_TIMEOUT = 10

# Sensor Configuration
SENSOR_CONFIG = [
    {
        'name': 'seat',
        'enable': True,
        'port': '/dev/ttyUSB0',
        'baud': 115200,
        'timeout': 0.5,
        'message': 'seat occupied',
        'debounce': 5
    },
    {
        'name': 'trunk',
        'enable': False,
        'port': '/dev/ttyUSB1',
        'baud': 115200,
        'timeout': 0.5,
        'message': 'trunk open',
        'debounce': 5
    },
]
