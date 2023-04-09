import time

from ant.core import driver
from ant.core.node import Node, Network
from ant.core.constants import NETWORK_KEY_ANT_PLUS, NETWORK_NUMBER_PUBLIC
from ant.plus.heartrate import *
from ant.plus.power import *
from ant.plus.speed_cadence import *
from ant.core import log
from ant.core.exceptions import ANTException, NodeError

from collections import deque
from statistics import mean

WHEEL_CIRCUMFERENCE = 2.2 # meters

class AntPlus:
    def __init__(self):
        self.speed = 0.0
        self.total_distance = 0.0
        self.instantaneous_power = 0
        self.average_power = 0
        self.cadence = 0.0
        self.heart_rate = 0

        self.avg_power_tracker = deque([0,0,0,0,0,0,0,0,0,0], maxlen=10)

    def start(self):
        #-------------------------------------------------#
        #  ANT Callbacks                                  #
        #-------------------------------------------------#
        def device_paired(device_profile, channel_id):
            print(f'Connected to { device_profile.name } ({ channel_id.deviceNumber })')

        def search_timed_out(device_profile):
            print(f'Could not connect to { device_profile.name }. Timed out')

        def channel_closed(device_profile):
            print(f'Channel closed for { device_profile.name }')

        def heart_rate_data(computed_heartrate, event_time_ms, rr_interval_ms):
            self.heart_rate = computed_heartrate
            print(f"Heart rate: { self.heart_rate }")

        def power_sensor_data(event_count, pedal_power_ratio, cadence, accumulated_power, instantaneous_power):
            self.instantaneous_power = instantaneous_power
            # self.cadence = cadence
            self.avg_power_tracker.append(instantaneous_power)
            self.average_power = mean(self.avg_power_tracker)
            # print(f"Instantaneous power: {self.instantaneous_power}, Average power: {self.average_power}")

        def speed_data(speed, distance):
            if speed is not None:
                self.speed = speed
                self.total_distance += distance
                # print(f"Speed: {(self.speed):.1f}km/h, Distance: {(self.total_distance):.1f}m")

        def cadence_data(cadence):
            if cadence is not None:
                self.cadence = cadence
                # print(f"Cadence: {(self.cadence):.0f}")

        self.antnode = Node(driver.USB2Driver())
        try:
            print("Starting ANT node")
            self.antnode.start()
            network = Network(key=NETWORK_KEY_ANT_PLUS, name='N:ANT+')
            self.antnode.setNetworkKey(NETWORK_NUMBER_PUBLIC, network=network)
            
            print("Creating Heart Rate Monitor")
            self.heartRateMonitor = HeartRate(self.antnode, network,
                               {'onDevicePaired' : device_paired,
                                'onSearchTimeout': search_timed_out,
                                'onChannelClosed': channel_closed,
                                'onHeartRateData': heart_rate_data})
            print("Creating Power Sensor")
            self.powerSensor = BicyclePower(self.antnode, network,
                               {'onDevicePaired' : device_paired,
                                'onSearchTimeout': search_timed_out,
                                'onChannelClosed': channel_closed,
                                'onPowerData'    : power_sensor_data})
            print("Creating Speed/Cadence Sensor")
            self.speedCadenceSensor = SpeedCadence(self.antnode, network, WHEEL_CIRCUMFERENCE,
                               {'onDevicePaired' : device_paired,
                                'onSearchTimeout': search_timed_out,
                                'onChannelClosed': channel_closed,
                                'onSpeedData'    : speed_data,
                                'onCadenceData'  : cadence_data})
            print("ANT init successful")
        except ANTException as err:
            print(f'Could not start ANT node\n{ err }')
            raise

    # Opens all the relevant ANT channels and begins listening to the specified devices
    def open(self):
        try:
            # Open channel and search for specified device types
            print("Opening Heartrate Monitor")
            self.heartRateMonitor.open()
            print("Opening Power Sensor")
            self.powerSensor.open()
            print("Opening Speed/Cadence Sensor")
            self.speedCadenceSensor.open()

            print('ANT started. Connecting to devices...')
        except ANTException as err:
            print(f'An error occured when attempting to open ANT channels\n{err}')

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

    # Closes the ANT node and performs cleanup
    def close(self):
        print("Closing ANT channels")
        try:
            self.heartRateMonitor.close()
            self.powerSensor.close()
            self.speedCadenceSensor.close()

            print("Stopping ANT node")
            self.antnode.stop()
        except NodeError as ne:
            print(ne)


if __name__ == "__main__":
    ant = AntPlus()
    ant.start()
    ant.open()
    ant.close()
