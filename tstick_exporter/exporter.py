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
import os
import faulthandler

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
from prometheus_client.registry import Collector

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

# Add Signal Handler
class SignalHandler():
    def __init__(self):
        self.shutdownCount = 0

        # Register signal handler
        signal.signal(signal.SIGINT, self._on_signal_received)
        signal.signal(signal.SIGTERM, self._on_signal_received)

    def is_shutting_down(self):
        return self.shutdownCount > 0

    def _on_signal_received(self, signal, frame):
        if self.shutdownCount > 1:
            logger.warning("Forcibly killing exporter")
            sys.exit(1)
        logger.info("Exporter is shutting down")
        self.shutdownCount += 1

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

# Create custom collector
class TStickCollector(Collector):
    def __init__(self):
        self.metrics = []
        self.prev = 0

    def update(self,metrics):
        # Update the metrics stored in the collector class
        tmp = self.metrics
        tmp.extend(metrics)
        self.metrics = tmp
    
    def collect(self):       
        # Send latest time
        now = time.time()
        tmp = []

        # Update global time
        tmp.append(
                {
                    "name": "tstick_global_time",
                    "value": now,
                    "help": "Battery current in mA"
                }
        )

        # add it to metrics
        self.metrics.extend(tmp)

        # collect metrics and send to prometheus
        for metric in self.metrics:
            name = metric["name"]
            value = metric["value"]
            help_text = metric.get("help","")
            labels = metric.get("labels", {})

            prom_metric = GaugeMetricFamily(name, help_text, labels = labels.keys())
            prom_metric.add_metric(value=value, labels=labels.values())
            yield prom_metric
            logger.debug(prom_metric)
        
        # empty metrics again for next request
        self.metrics = []

tstickCollector = TStickCollector()

def get_tstick_battery_current(address: str, *args: List[Any]) -> None:
    # Print OSC address
    logger.debug(address)

    # get time
    now = time.time()

    # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]

    # append battery data
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

    # append local time
    metrics.append(
            {
                "name": "tstick_local_time",
                "value": now,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "current local counter"
            }
    )
    tstickCollector.update(metrics)

def get_tstick_battery_voltage(address: str, *args: List[Any]) -> None:
    # Print OSC address
    logger.debug(address)

    # get time
    now = time.time()

    # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]

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

    # append local time
    metrics.append(
            {
                "name": "tstick_local_time",
                "value": now,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "current local counter"
            }
    )

    tstickCollector.update(metrics)

def get_tstick_battery_percentage(address: str, *args: List[Any]) -> None:
    # Print OSC address
    logger.debug(address)

    # get time
    now = time.time()

    # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]

    # append battery data
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

    # append local time
    metrics.append(
            {
                "name": "tstick_local_time",
                "value": now,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "current local counter"
            }
    )

    tstickCollector.update(metrics)

def get_tstick_battery_tte(address: str, *args: List[Any]) -> None:
    # Print OSC address
    logger.debug(address)

    # get time
    now = time.time()

    # Set up empty metrics array
    metrics = []

    # Parce the OSC message for the tstick ID
    tstickID = address[1:11]

    # append battery data
    metrics.append(
            {
                "name": "tstick_battery_tte",
                "value": args[0],
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "Battery time to empty (hours)"
            }
    )

    # append local time
    metrics.append(
            {
                "name": "tstick_local_time",
                "value": now,
                "labels": {
                    "tstickID": tstickID,

                },
                "help": "current local counter"
            }
    )

    tstickCollector.update(metrics)

def main():
    #initialise Logger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime) %(levelname) %(message)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel("INFO")  # set logger level

    # Read config
    config = {
        "osc_port": int(get_config_value("OSC_PORT", "8080")),
        "exporter_port": int(get_config_value("EXPORTER_PORT", "8000")),
        "log_level": get_config_value("EXPORTER_LOG_LEVEL", "INFO"),
    }

    ip = "0.0.0.0"
    osc_port = config["osc_port"]
    exporter_port = config["exporter_port"]
    logger.setLevel(config["log_level"])  # set logger level

    
    # Register signal handler
    signal_handler = SignalHandler()

    # Register metrics
    REGISTRY.register(tstickCollector)
    
    # Start Prometheus server
    start_http_server(exporter_port)

    # Set up dispatcher
    disp.map("/TStick_*/battery/current*",get_tstick_battery_current)
    disp.map("/TStick_*/battery/voltage*",get_tstick_battery_voltage)
    disp.map("/TStick_*/battery/percentage*",get_tstick_battery_percentage)
    disp.map("/TStick_*/battery/tte*",get_tstick_battery_tte)

    # Set up OSC Server
    server = osc_server.ThreadingOSCUDPServer((ip,osc_port),disp)
    logger.info("Server on {}".format(server.server_address))
    server.serve_forever()

    # run forever
    while not signal_handler.is_shutting_down():
        time.sleep(1)
    
    # shutdown text
    logger.info("Exporter has shutdown")

if __name__ == "__main__":
    main()
