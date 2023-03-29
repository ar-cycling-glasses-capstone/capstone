import RPi.GPIO as GPIO
import pygame
import time
import util

class Display:

    ASSETS_PATH = "./assets/"
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self):
        pygame.init()

        # CLASS VARIABLES
        self.hud_toggles = {
            "blindspot": True,
            "biometrics": True,
            "weather": True,
            "bike_stats": True,
        }

        

        self.done = False
        self.width  = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

        # LAUNCH IMAGE
        self.image0 = pygame.image.load(Display.ASSETS_PATH + "Lum_For_Ants.jpg")
        self.image0 = pygame.transform.scale(image0, (self.width, self.height))



    def main(self):
        self.init_display();

        time.sleep(5)

        self.main_loop();

        sys.exit();

    def init_display(self):
        self.screen = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
        self.screen.blit(image0,(0,0))
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
        print("check from app...")
        time.sleep(1)

    def check_updates_from_camera(self):
        print("check from camera...")
        time.sleep(1)

    def check_updates_from_antreceiver(self):
        print("check from ant+...")
        time.sleep(1)

    def update_display(self):
        print("updating display...")
        

        # TEST FONTS
        font0 = pygame.font.Font('freesansbold.ttf', 32)
        text0 = font.render('Test', True, Display.BLACK)
        font1 = pygame.font.Font('freesansbold.ttf', 64)
        text1 = font.render('Test', True, Display.BLACK)
        font2 = pygame.font.Font('freesansbold.ttf', 96)
        text2 = font.render('Test', True, Display.BLACK)

        self.display.fill(Display.WHITE)
        self.display.blit(text0, (10, 100));
        self.display.blit(text1, (10, 200));
        self.display.blit(text2, (10, 300));

        # UPDATE BLINDSPOT
        if (self.hud_toggles["blindspot"]):
            pass
        else:
            pass
        
        # UPDATE WEATHER
        if (self.hud_toggles["weather"]):
            pass
        else:
            pass
        
        # UPDATE BIKE STATS
        if (self.hud_toggles["bike_stats"]):
            pass
        else:
            pass
        
        # UPDATE BIOMETRICS
        if (self.hud_toggles["biometrics"]):
            pass
        else:
            pass


        pygame.display.update()

if __name__ == "__main__":
    display = Display()
    display.main()
