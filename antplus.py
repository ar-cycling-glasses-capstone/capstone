"""
Example of using mulitple devices: a PowerMeter and FitnessEquipment.

Also demos Workout feature of FitnessEquipment, where the device has a thread and sends info to the master.

Refer to subparsers/influx for another example of creating multiple devices at runtime
"""
import math
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.power_meter import PowerMeter, PowerData
from openant.devices.heart_rate import HeartRate, HeartRateData
from openant.devices.bike_speed_cadence import (
    BikeSpeed,
    BikeCadence,
    BikeSpeedCadence,
    BikeSpeedData,
    BikeCadenceData
)
from openant.devices.fitness_equipment import (
    FitnessEquipment,
    FitnessEquipmentData,
    Workout,
)

class AntPlus:
    def __init__(self, wheel_circumference):
        self.wheel_circumference = wheel_circumference
        print(f"Initializing ANT+ node with wheel circumference {self.wheel_circumference}mm")
        import logging
        logging.basicConfig(level=logging.INFO)

        self.node = Node()
        self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        self.power = 0
        self.avg_power = 0
        self.speed = 0
        self.cadence = 0
        self.heart_rate = 0

        # Append multiple devices if needed (ex: powermeter, cadence sensor, heart-rate monitor, etc)
        # The Computrainer we're using if broadcast as an ANT-FS device because it technically isn't
        # an ANT+ device and we're using software to bridge it to ANT+. As an ANT-FS device it
        # broadcasts power, cadence, and speed (as a Computrainer would (no heartrate :'( tho))
        # Pretty sure we can control resistance as well?
        self.devices = []
        # self.devices.append(BikeSpeed(self.node))
        # self.devices.append(HeartRate(self.node, 8962, "Garmin HRM"))
        # self.devices.append(PowerMeter(self.node, 63759, "CycleOps Powertap"))
        self.devices.append(HeartRate(self.node))
        self.devices.append(PowerMeter(self.node))
        self.devices.append(BikeSpeedCadence(self.node))
        # self.devices.append(FitnessEquipment(self.node))

        def on_found(device):
            print(f"Device {device} found and receiving")

            #if type(device) == FitnessEquipment and len(workouts) > 0:
            #    device.start_workouts(workouts)

        def on_device_data(page: int, page_name: str, data):
            if isinstance(data, BikeSpeedData):
                speed = data.calculate_speed(2.3)
                if speed:
                    self.speed = speed
                    print("Speed Sensor: ")
                    print(f" Speed: {self.speed:.2f} km/h")

            elif isinstance(data, BikeCadenceData):
                cadence = data.cadence
                if cadence:
                    self.cadence = cadence
                    print("Cadence Sensor: ")
                    print(f" Cadence: {self.cadence:.2f} rpm")

            elif isinstance(data, PowerData):
                self.power = data.instantaneous_power
                self.avg_power = data.average_power
                # self.cadence = data.cadence
                #print(f"PowerMeter {page_name} ({page}) update: {data}\n")
                print("PowerMeter:")
                print(f" Instantaneous Power: {self.power} W")
                print(f" Average Power:       {self.avg_power} W")
                #print(f" Torque:              {data.torque}")
                #print(f" Angular Velocity:    {data.angular_velocity}")
                # print(f" Cadence:             {self.cadence}");
                
            elif isinstance(data, HeartRateData):
                self.heart_rate = data.heart_rate
                print("HeartRate Sensor:")
                print(f" HeartRate:           {self.heart_rate} bpm")

            # elif isinstance(data, FitnessEquipmentData):
            #     # self.speed = round(2*math.pi*(self.wheel_circumference/1000.0)*data.speed, 2)
            #     print(f"FitnessEquipment Sensors:")
            #     print(f" Type:                {data.type}")
            #     print(f" Resistance:          {data.resistance}")
            #     #print(f" Capabilities:        {data.capabilities}")
            #     print(f" Speed:               {self.speed} km/h")
            #     #print(f" Incline:             {data.incline}")
            #     #print(f" Target Resistance:   {data.target_resistance}")
            #     #print(f"FitnessEquipment {page_name} ({page}) update: {data}\n")
            print()

        # Set callbacks
        for d in self.devices:
            # d.on_found = lambda: on_found(d)
            d.on_found = lambda: on_found(d)
            d.on_device_data = on_device_data

    def start_ant(self):
        try:
            print(f"Starting {self.devices}, press Ctrl-C to finish")
            self.node.start()
        # except Exception as e:
        #     print("An exception occured...")
        #     print(e)
        except KeyboardInterrupt:
             print("Closing ANT+ device...")
        finally:
            self.close_ant()

    def close_ant(self):
        for d in self.devices:
            d.close_channel()
        self.node.stop()


if __name__ == "__main__":
    ant = AntPlus(575)
    ant.start_ant()
