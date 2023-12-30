#requirements:
#python-osc
#wmill
#requests
#prometheus-client
#python-json-logger

import time
import os
import sys
import signal
import faulthandler

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

# logging
import logging
from pythonjsonlogger import jsonlogger

# OSC packages
from pythonosc.dispatcher import Dispatcher
from typing import List, Any

# Setup server
from pythonosc import osc_server

# Enable loging
faulthandler.enable()
logger = logging.getLogger()

# Initiate Dispatcher
disp = Dispatcher()

# Get value from config
def get_config_value(key, default=""):
    input_path = os.environ.get("FILE__" + key, None)
    if input_path is not None:
        try:
            with open(input_path, "r") as input_file:
                return input_file.read().strip()
        except IOError as e:
            logger.error(f"Unable to read value for {key} from {input_path}: {str(e)}")

    return os.environ.get(key, default)

def collect(metrics):
    # collect metrics and send to prometheus
    for metric in metrics:
        name = metric["name"]
        value = metric["value"]
        help_text = metric.get("help","")
        labels = metric.get("labels", {})

        prom_metric = GaugeMetricFamily(name, help_text, labels = labels.keys())
        prom_metric.add_metric(value=value, labels=labels.values())
        yield prom_metric
        logger.info(prom_metric)


def get_tstick_battery_data(address: str, *args: List[Any]) -> None:
    # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]

    # Parse which propery
    battery_property = address[20:]
    # append battery data
    if (battery_property == "current"):
        metrics.append(
                {
                    "name": "tstick_battery_current",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "Battery current in mA"
                }
        )
    
    if (battery_property == "voltage"):
        metrics.append(
                {
                    "name": "tstick_battery_voltage",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "Battery voltage in V"
                }
        )
    
    if (battery_property == "percentage"):
        metrics.append(
                {
                    "name": "tstick_battery_percentage",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "Battery percentage"
                }
        )
    print(metrics)
    collect(metrics)

def get_tstick_raw_data(address: str, *args: List[Any]) -> None:
        # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]
    
    # Parce the arguments
    raw_property = address[16:]


    if (raw_property == "fsr"):
        metrics.append(
                {
                    "name": "tstick_fsr",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "raw FSR value"
                }
        )
    if (raw_property == "accl"):
        metrics.append(
                {
                    "name": "tstick_acclx",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "Raw accelerometer x-axis data (m/s/s)"
                }
        )
        metrics.append(
                {
                    "name": "tstick_accly",
                    "value": args[1],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help":  "Raw accelerometer y-axis data (m/s/s)"
                }
        )
        metrics.append(
                {
                    "name": "tstick_acclz",
                    "value": args[2],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help":  "Raw accelerometer z-axis data (m/s/s)"
                }
        )        
    if (raw_property == "gyro"):
        metrics.append(
                {
                    "name": "tstick_gyrox",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "Raw gyrometer x-axis data (deg/s)"
                }
        )
        metrics.append(
                {
                    "name": "tstick_gyroy",
                    "value": args[1],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help":  "Raw gyrometer y-axis data (deg/s)"
                }
        )
        metrics.append(
                {
                    "name": "tstick_gyroz",
                    "value": args[2],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help":  "Raw gyrometer z-axis data (deg/s)"
                }
        )   
    if (raw_property == "magn"):
        metrics.append(
                {
                    "name": "tstick_magnx",
                    "value": args[0],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help": "Raw magnetometer x-axis data (uT)"
                }
        )
        metrics.append(
                {
                    "name": "tstick_magny",
                    "value": args[1],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help":  "Raw magnetometer y-axis data (uT)"
                }
        )
        metrics.append(
                {
                    "name": "tstick_magnz",
                    "value": args[2],
                    "labels": {
                        "tstickID": tstickID,

                    },
                    "help":  "Raw magnetometer z-axis data (uT)"
                }
        )   
    if (raw_property == "capsense"):
        for n in range(len(args)):
            metrics.append(
                    {
                        "name": f"tstick_capsense_{n}",
                        "value": args[n],
                        "labels": {
                            "tstickID": tstickID,

                        },
                        "help": f"Raw capsense data for sensor {n}"
                    }
            )
    print(metrics)
    collect(metrics)

def get_tstick_ypr(address: str, *args: List[Any]) -> None:
    # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]

    # Parse ypr
    yaw = args[0]
    pitch = args[1]
    roll = args[2]

    # append to metric
    metrics.append(
            {
                "name": "tstick_yaw",
                "value": yaw,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "T-Stick yaw in radians"
            }
    )
    metrics.append(
            {
                "name": "tstick_pitch",
                "value": pitch,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "T-Stick pitch in radians"
            }
    )
    metrics.append(
            {
                "name": "tstick_roll",
                "value": roll,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "T-Stick roll in radians"
            }
    )
    print(metrics)
    collect(metrics)

def main():
    config = {
        "osc_port": get_config_value("OSC_PORT", ""),
        "exporter_port": int(get_config_value("EXPORTER_PORT", "8000")),
        "log_level": get_config_value("EXPORTER_LOG_LEVEL", "INFO"),
    }

    ip = "127.0.0.1"
    osc_port = config["osc_port"]
    exporter_port = config["exporter_port"]

    #initialise Logger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime) %(levelname) %(message)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(config["log_level"])  # default until config is loaded
    
    # Start Prometheus server
    start_http_server(exporter_port)

    # Set up dispatcher
    disp.map("/TStick_*/battery/*",get_tstick_battery_data)
    disp.map("/TStick_*/raw/*",get_tstick_raw_data)
    disp.map("/TStick_*/ypr*",get_tstick_ypr)

    # Set up OSC Server
    server = osc_server.ThreadingOSCUDPServer((ip,osc_port),disp)
    print("Servering on {}".format(server.server_address))
    server.serve_forever()


