import RPi.GPIO as GPIO
import pygame
import time
import util
from operator import add

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

    def __init__(self):
        pygame.init()

        # CLASS VARIABLES
        self.hud_toggles = {
            "blindspot": True,
            "biometrics": True,
            "weather": True,
            "bike_stats": True,
        }

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

        self.main_loop();

        pygame.quit()
        quit()

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
            
            self.check_updates_from_app(); # Interface with Felix
            self.check_updates_from_camera(); # Interface with Sabrina
            self.check_updates_from_antreceiver(); # Interface with Alex
            self.update_display();

    def check_updates_from_app(self):
        pass

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
            pass

        
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
