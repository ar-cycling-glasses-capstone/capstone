import RPi.GPIO as GPIO
import pygame
import time
import util
from operator import add
from bluetooth_server import srv
from antplus import AntPlus
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
    FONT_SIZE = 96

    # POSITIONS
    PADDING = 50

    WIDTH = pygame.display.Info().current_w
    HEIGHT = pygame.display.Info().current_h

    ICON_SIZE = (200, 200)

    BIKE_STATS_POSITION = (10, 10)
    BLINDSPOT_POSITION = (WIDTH - 200, 10)
    WEATHER_POSITION = (10, HEIGHT - 200)
    BIOMETRICS_POSITION = (WIDTH - 300, HEIGHT - 100)

    def __init__(self):
        pygame.init()

        # CLASS VARIABLES
        self.hud_toggles = {
            "blindspot": True,
            "biometrics": True,
            "weather": True,
            "bike_stats": True,
        }

        self.weather = {
            "temperature": 21,
            "wind_speed": 5,
            "condition": "rainy"
        }

        # Start bluetooth server on a different thread
        self.thread_list = []


        self.font = pygame.font.Font(Display.FONT, Display.FONT_SIZE)

        self.done = False
        self.width  = Display.WIDTH
        self.height = Display.HEIGHT

        # LAUNCH IMAGE
        self.launch_image = pygame.image.load(Display.ASSETS_PATH + Display.LAUNCH_IMAGE)
        self.launch_image = pygame.transform.scale(self.launch_image, (self.width, self.height))

        # BLINDSPOT IMAGE
        self.warning_image = pygame.image.load(Display.ASSETS_PATH + Display.WARNING_IMAGE)
        self.warning_image = pygame.transform.scale(self.warning_image, Display.ICON_SIZE)



        # TEMP WEATHER ICONS
        sunny_icon = pygame.image.load(Display.ASSETS_PATH + Display.SUNNY_ICON)
        rainy_icon = pygame.image.load(Display.ASSETS_PATH + Display.RAINY_ICON)
        windy_icon = pygame.image.load(Display.ASSETS_PATH + Display.WINDY_ICON)

        sunny_icon = pygame.transform.scale(sunny_icon, Display.ICON_SIZE)
        rainy_icon = pygame.transform.scale(rainy_icon, Display.ICON_SIZE)
        windy_icon = pygame.transform.scale(windy_icon, Display.ICON_SIZE)

        self.weather_icons = {
            "sunny": sunny_icon,
            "rainy": rainy_icon,
            "windy": windy_icon
        };



    def main(self):
        self.ant = self.init_ant(Display.WHEEL_CIRCUMFERENCE)
        self.start_ant()

        self.init_display();

        time.sleep(1)
        
        # self.create_server()
        self.main_loop();

        self.ant.close_ant();
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
                recvd_data = server.get_info();
            
                self.hud_toggles = recvd_data["hud_toggles"];
                self.weather_data = recvd_data["weather"];
            except Exception as msg:
                print(msg)

    def init_ant(self, wheel_circ):
        return AntPlus(wheel_circ)

    def start_ant(self):
        new_thread = threading.Thread(target=self.ant_runner, args=())

        # Record the new thread                                        
        self.thread_list.append(new_thread)

        # Start the new thread running
        print("Starting serving thread: ", new_thread.name)
        new_thread.daemon = True
        new_thread.start()

    def ant_runner(self):
        self.ant.start_ant();


    def init_display(self):
        # self.screen = pygame.display.set_mode((0, 0),pygame.NOFRAME)
        self.screen = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode((0, 0))
        self.screen.blit(self.launch_image,(0,0))
        pygame.display.update()

    def main_loop(self):
        while(not self.done):
            for event in pygame.event.get():
                # Kill program if QUIT event or Escape key pressed
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.done = True
            
            # self.check_updates_from_camera();
            self.update_display();

    def update_display(self):
        self.screen.fill(Display.BLACK)

        # UPDATE BLINDSPOT
        if (self.hud_toggles["blindspot"]):
            self.screen.blit(self.warning_image, Display.BLINDSPOT_POSITION)
        
        # UPDATE WEATHER
        if (self.hud_toggles["weather"]):
            weather_pos_x, weather_pos_y = Display.WEATHER_POSITION

            temp = self.weather["temperature"]
            wind_speed = self.weather["wind_speed"]
            condition = self.weather["condition"]

            weather_text = str(temp) + "C"

            # Render Image
            self.screen.blit(self.weather_icons[condition], (weather_pos_x, weather_pos_y))
            
            # Render Text
            util.render_text(self.screen, self.font, weather_text, Display.WHITE,
                            (weather_pos_x + 220, weather_pos_y + 100))

        
        # UPDATE BIKE STATS
        if (self.hud_toggles["bike_stats"]):
            stats_pos_x, stats_pos_y = Display.BIKE_STATS_POSITION

            speed_text = str(self.ant.speed) + "km/h"
            distance_text = str(1000) + "km"
            cadence_text = str(self.ant.cadence) + "RPM"
            wattage_text = str(self.ant.power) + "W"

            util.render_text(self.screen, self.font, speed_text, Display.WHITE,
                            (stats_pos_x, stats_pos_y + 0))
            util.render_text(self.screen, self.font, distance_text, Display.WHITE,
                            (stats_pos_x, stats_pos_y + 80))
            util.render_text(self.screen, self.font, cadence_text, Display.WHITE,
                            (stats_pos_x, stats_pos_y + 160))
            util.render_text(self.screen, self.font, wattage_text, Display.WHITE,
                            (stats_pos_x, stats_pos_y + 240))
        
        # UPDATE BIOMETRICS
        if (self.hud_toggles["biometrics"]):
            bio_pos_x, bio_pos_y = Display.BIOMETRICS_POSITION

            heart_rate_text = str(self.ant.heart_rate) + "BPM"

            util.render_text(self.screen, self.font, heart_rate_text, Display.WHITE,
                            (bio_pos_x, bio_pos_y))


        pygame.display.update()

if __name__ == "__main__":
    display = Display()
    display.main()
