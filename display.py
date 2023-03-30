import RPi.GPIO as GPIO
import pygame
import time
import util
from operator import add
from bluetooth_server import srv
import threading

class Display:

    ASSETS_PATH = "./assets/"
    LAUNCH_IMAGE = "Lum_For_Ants.jpg"
    WARNING_IMAGE = "warning.png"

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    FONT = 'freesansbold.ttf'
    FONT_SIZE = 48

    # POSITIONS
    BIKE_STATS_POSITION = (10, 10)
    BLINDSPOT_POSITION = (820, 20)
    WEATHER_POSITION = (10, 400)

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
            "condition": "sunny"
        }

        # Start bluetooth server on a different thread
        self.thread_list = []

        self.font = pygame.font.Font(Display.FONT, Display.FONT_SIZE)
        

        self.done = False
        self.width  = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

        # LAUNCH IMAGE
        self.launch_image = pygame.image.load(Display.ASSETS_PATH + Display.LAUNCH_IMAGE)
        self.launch_image = pygame.transform.scale(self.launch_image, (self.width, self.height))

        # BLINDSPOT IMAGE
        self.warning_image = pygame.image.load(Display.ASSETS_PATH + Display.WARNING_IMAGE)
        self.warning_image = pygame.transform.scale(self.warning_image, (120, 120))



    def main(self):
        self.init_display();

        time.sleep(1)
        
        self.create_server()
        self.main_loop();

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


    def init_display(self):
        self.screen = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
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
            
            self.check_updates_from_camera(); # Interface with Sabrina
            self.check_updates_from_antreceiver(); # Interface with Alex
            self.update_display();


    def check_updates_from_camera(self):
        pass

    def check_updates_from_antreceiver(self):
        pass

    def update_display(self):
        self.screen.fill(Display.WHITE)

        # UPDATE BLINDSPOT
        if (self.hud_toggles["blindspot"]):
            self.screen.blit(self.warning_image, Display.BLINDSPOT_POSITION)
        
        # UPDATE WEATHER
        if (self.hud_toggles["weather"]):
            weather_pos = Display.WEATHER_POSITION

            temp = self.weather["temperature"]
            wind_speed = self.weather["wind_speed"]
            condition = self.weather["condition"]

            weather_text = str(temp) + "C"
            if (condition == "sunny"):
                util.load_svg(Display.ASSETS_PATH + "wi-day-sunny.svg", self.screen, weather_pos, (120, 120))
            elif(condition == "cloudy"):
                pass
            elif (condition == "rainy"):
                pass
            elif (condition == "snowy"):
                pass
            elif (condition == "windy"):
                pass
            
            util.render_text(self.screen, self.font, weather_text, Display.BLACK,
                            (weather_pos[0] + 140, weather_pos[1]))

        
        # UPDATE BIKE STATS
        if (self.hud_toggles["bike_stats"]):
            stats_pos = Display.BIKE_STATS_POSITION

            speed_text = "Speed: " + str(200) + "km/h"
            distance_text = "Distance: " + str(1000) + "km"
            cadence_text = "Cadence: " + str(99999)
            wattage_text = "Wattage: " + str(120) + "W" 

            util.render_text(self.screen, self.font, speed_text, Display.BLACK,
                            (stats_pos[0], stats_pos[1] + 0))
            util.render_text(self.screen, self.font, distance_text, Display.BLACK,
                            (stats_pos[0], stats_pos[1] + 40))
            util.render_text(self.screen, self.font, cadence_text, Display.BLACK,
                            (stats_pos[0], stats_pos[1] + 80))
            util.render_text(self.screen, self.font, wattage_text, Display.BLACK,
                            (stats_pos[0], stats_pos[1] + 120))
        
        # UPDATE BIOMETRICS
        if (self.hud_toggles["biometrics"]):
            pass
        else:
            pass


        pygame.display.update()

if __name__ == "__main__":
    display = Display()
    display.main()
