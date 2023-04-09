import RPi.GPIO as GPIO
import pygame
import time
import util
from operator import add
from bluetooth_server import srv
from antplus import antplus
from ant.core.exceptions import ANTException
import threading


class Display:
    pygame.init()

    ASSETS_PATH = "./assets/"
    LAUNCH_IMAGE = "Lum_For_Ants.jpg"
    WARNING_IMAGE = "warning.png"
    SUNNY_ICON = "noun-sunny-1038993.png"
    RAINY_ICON = "noun-rainy-2288476.png"
    WINDY_ICON = "noun-wind-blow-2288438.png"

    WHEEL_CIRCUMFERENCE = 570

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    FONT = 'freesansbold.ttf'
    FONT_SIZE = 84
    BLINDSPOT_FONT_SIZE = 48

    # POSITIONS
    WIDTH = pygame.display.Info().current_w
    HEIGHT = pygame.display.Info().current_h

    ICON_SIZE = (120, 120)

    def __init__(self):
        pygame.init()

        # CLASS VARIABLES
        self.hud_toggles = {
            "blindspot": True,
            "biometrics": True,
            "weather": True,
            "bike_stats": True,
            "timer": True,
            # "altitude": True,
        }

        # center, centery, centerx,
        # midbottom, midleft, midright, midtop,
        # bottomleft, bottomright,
        # topright, topleft
        self.hud_custom = {
            "align": {
                "blindspot": "midtop",
                "biometrics": "bottomright",
                "weather": "topright",
                "bike_stats": "topleft",
                "timer": "bottomleft"
            },
            "offset": {
                "blindspot": (20, 20),
                "biometrics": (20, 20),
                "weather": (20, 20),
                "bike_stats": (20, 20),
                "timer": (20, 20)
            },
            "spacing": {
                "blindspot": 20,
                "biometrics": 20,
                "weather": 80,
                "bike_stats": -30,
                "timer": 0
            }
        }

        self.weather_data = {
            "dateTime": "2023-04-07T20:53:00-04:00",
            "phrase": "Sunny",
            "hasPrecipitation": False,
            "temperature": {
                "value": 2.2,
                "unit": "C",
                "unitType": 17
            },
            "realFeelTemperature": {
                "value": -2.0,
                "unit": "C",
                "unitType": 17
            },
            "wind": {
                "direction": {
                    "degrees": 315.0,
                    "localizedDescription": "NW"
                },
                "speed": {
                    "value": 14.8,
                    "unit": "km/h",
                    "unitType": 7
                }
            }
        }

        # Start bluetooth server on a different thread
        self.thread_list = []

        self.font = pygame.font.Font(Display.FONT, Display.FONT_SIZE)
        self.blindspot_font = pygame.font.Font(Display.FONT, Display.BLINDSPOT_FONT_SIZE)

        self.done = False
        self.width = Display.WIDTH
        self.height = Display.HEIGHT

        # LAUNCH IMAGE
        self.launch_image = pygame.image.load(
            Display.ASSETS_PATH + Display.LAUNCH_IMAGE)
        self.launch_image = pygame.transform.scale(
            self.launch_image, (self.width, self.height))

        # BLINDSPOT IMAGE
        self.warning_image = pygame.image.load(
            Display.ASSETS_PATH + Display.WARNING_IMAGE)
        self.warning_image = pygame.transform.scale(
            self.warning_image, Display.ICON_SIZE)

        # TEMP WEATHER ICONS
        sunny_icon = pygame.image.load(
            Display.ASSETS_PATH + Display.SUNNY_ICON)
        rainy_icon = pygame.image.load(
            Display.ASSETS_PATH + Display.RAINY_ICON)
        windy_icon = pygame.image.load(
            Display.ASSETS_PATH + Display.WINDY_ICON)

        sunny_icon = pygame.transform.scale(sunny_icon, Display.ICON_SIZE)
        rainy_icon = pygame.transform.scale(rainy_icon, Display.ICON_SIZE)
        windy_icon = pygame.transform.scale(windy_icon, Display.ICON_SIZE)

        self.weather_icons = {
            "Sunny": sunny_icon,
            "Rainy": rainy_icon,
            "Windy": windy_icon
        }

    def main(self):
        self.init_ant()
        self.start_ant()

        self.init_display()

        time.sleep(1)

        self.create_server()
        self.main_loop()

        pygame.quit()
        quit()

    def create_server(self):
        new_thread = threading.Thread(target=self.runner,
                                      args=())

        # Record the new thread.
        self.thread_list.append(new_thread)

        # Start the new thread running.
        print("Starting serving thread: ", new_thread.name)
        new_thread.daemon = True
        new_thread.start()

    def runner(self):
        server = srv.Server()
        while True:
            try:
                server.main_loop()
                recvd_data = server.get_info()

                if recvd_data["hud_toggles"]:
                    self.hud_toggles = recvd_data["hud_toggles"]

                if recvd_data["weather"]:
                    self.weather_data = recvd_data["weather"]

                if recvd_data["timer"]:
                    pass

                server.send_data("hei")

            except Exception as msg:
                print(msg)

    # Initializes and creates ANT object
    def init_ant(self):
        self.ant = antplus.AntPlus()
    
    def start_ant(self):
        new_thread = threading.Thread(target=self.ant_runner, args=())

        # Record the new thread
        self.thread_list.append(new_thread)

        # Start the new thread running
        print("Starting serving thread: ", new_thread.name)
        new_thread.daemon = True
        new_thread.start()
    
    # Starts ANT node and 
    def ant_runner(self):
        try:
            self.ant.start()
            self.ant.open()
            self.ant.close()
        except ANTException:
            pass

    def init_display(self):
        # self.screen = pygame.display.set_mode((0, 0),pygame.NOFRAME)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.screen = pygame.display.set_mode((0, 0))
        self.screen.blit(self.launch_image, (0, 0))
        pygame.display.update()

    def main_loop(self):
        while (not self.done):
            for event in pygame.event.get():
                # Kill program if QUIT event or Escape key pressed
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.done = True

            # self.check_updates_from_camera();

            self.update_display()

    def update_display(self):
        self.screen.fill(Display.BLACK)

        # UPDATE BLINDSPOT
        people = 2
        cars = 0
        if (self.hud_toggles["blindspot"]):
            people_text = f"{(people)} P"
            car_text = f"{(cars)} C"
            util.render_img(self.screen,
                            self.warning_image,
                            self.hud_custom["offset"]["blindspot"],
                            self.hud_custom["align"]["blindspot"])

            util.render_text(self.screen, self.blindspot_font,
                             people_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["blindspot"],
                             self.hud_custom["align"]["blindspot"],
                             (0, 120)
                             )
            
            util.render_text(self.screen, self.blindspot_font,
                             car_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["blindspot"],
                             self.hud_custom["align"]["blindspot"],
                             (0, 160)
                             )

        # UPDATE WEATHER
        if (self.hud_toggles["weather"]):
            condition = self.weather_data["phrase"]

            weather_text = str(self.weather_data["realFeelTemperature"]["value"]) \
                + str(self.weather_data["realFeelTemperature"]["unit"])
            
            wind_text = str(self.weather_data["wind"]["speed"]["value"]) \
                + str(self.weather_data["wind"]["speed"]["unit"])

            # Render Image
            icon_rect = util.render_img(self.screen,
                                        self.weather_icons[condition],
                                        self.hud_custom["offset"]["weather"],
                                        self.hud_custom["align"]["weather"]
                                        )

            # Render Text
            util.render_text(self.screen, self.font,
                             weather_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["weather"],
                             self.hud_custom["align"]["weather"],
                             (0, 80+ self.hud_custom["spacing"]["weather"])
                             )
            
            util.render_text(self.screen, self.font,
                             wind_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["weather"],
                             self.hud_custom["align"]["weather"],
                             (0, 80+ self.hud_custom["spacing"]["weather"] * 2)
                             )

        # UPDATE BIKE STATS
        if (self.hud_toggles["bike_stats"]):
            speed_text = f"{(self.ant.speed):.1f}km/h"
            distance_text = f"{(self.ant.total_distance/1000):.1f}km"
            cadence_text = f"{(self.ant.cadence):.0f}rpm"
            wattage_text = f"{(self.ant.instantaneous_power):.0f}w"
            avg_wattage_text = f"{(self.ant.average_power):.0f}w avg"


            speed_rect = util.render_text(self.screen, self.font,
                             speed_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["bike_stats"],
                             self.hud_custom["align"]["bike_stats"],
                             (0,0)
                             )

            dist_rect = util.render_adjacent_text(self.screen,
                                      distance_text,
                                      self.font, Display.WHITE,
                                      self.hud_custom["spacing"]["bike_stats"],
                                      speed_rect,
                                      "bottom")

            avg_watt_rect = util.render_adjacent_text(self.screen,
                                      avg_wattage_text,
                                      self.font, Display.WHITE,
                                      self.hud_custom["spacing"]["bike_stats"],
                                      dist_rect,
                                      "bottom")

            cadence_rect = util.render_adjacent_text(self.screen,
                                      cadence_text,
                                      self.font, Display.WHITE,
                                      self.hud_custom["spacing"]["bike_stats"],
                                      avg_watt_rect,
                                      "bottom")

            wattage_rect = util.render_adjacent_text(self.screen,
                                      wattage_text,
                                      self.font, Display.WHITE,
                                      self.hud_custom["spacing"]["bike_stats"],
                                      cadence_rect,
                                      "bottom")

        # UPDATE BIOMETRICS
        if (self.hud_toggles["biometrics"]):
            heart_rate_text = f"{(self.ant.heart_rate)}bpm"

            util.render_text(self.screen, self.font,
                             heart_rate_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["biometrics"],
                             self.hud_custom["align"]["biometrics"],
                             (0,0)
                             )
        
        # UPDATE TIMER
        timer = "18:25.596"
        if (self.hud_toggles["timer"]):
            timer_text = f"{(timer)}"

            util.render_text(self.screen, self.font,
                             timer_text,
                             Display.WHITE,
                             self.hud_custom["offset"]["timer"],
                             self.hud_custom["align"]["timer"],
                             (0, 0)
                             )

        pygame.display.update()


if __name__ == "__main__":
    display = Display()
    display.main()
