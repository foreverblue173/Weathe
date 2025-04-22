import pygame
import sys
from CONFIG import SCREEN_WIDTH, SCREEN_HEIGHT

class VideoPlayer:
    def __init__(self):
        pygame.init()

        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        #pygame.display.set_caption("Basic Pygame Window")
        self.fullscreen = False 

        self.images_to_draw = []

        self.clock = pygame.time.Clock()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))

    def blit(self, surface, loc, type = "path", resize=False, size = None):
        if type == "path":
            surface = pygame.image.load(surface)

        if resize == "One":
            w = surface.get_width()
            h = surface.get_height()

            width_scale = SCREEN_WIDTH / w
            height_scale = SCREEN_HEIGHT / h
            scale = min(width_scale, height_scale)

            surface = pygame.transform.scale(surface, (w * scale, h * scale))
            
            if width_scale > height_scale:
                w = surface.get_width()
                location = ((SCREEN_WIDTH-w)/2,0)
            else:
                h = surface.get_height()
                location = (0, (SCREEN_HEIGHT-h)/2)
        
        elif resize == "Four":
            """
            if location == "topLeft":
                location = (0,0)
            elif location == "topRight":
                location = (SCREEN_WIDTH/2,0)
            elif location == "bottomLeft":
                location = (0,SCREEN_HEIGHT/2)
            elif location == "bottomRight":
                location = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            """

            w = surface.get_width()
            h = surface.get_height()

            sw = SCREEN_WIDTH / 2
            sh = SCREEN_HEIGHT / 2

            width_scale = sw / w
            height_scale = sh / h
            scale = min(width_scale, height_scale)

            surface = pygame.transform.scale(surface, (int(w * scale), int(h * scale)))
            
            if width_scale > height_scale:
                w = surface.get_width()
                if loc == "topLeft":
                    location = ((sw-w)/2,0)
                elif loc == "topRight":
                    location = (sw + (sw-w)/2,0)
                elif loc == "bottomLeft":
                    location = ((sw-w)/2,sh)
                elif loc == "bottomRight":
                    location = (sw + (sw-w)/2,sh)
                #location = ((sw-w)/2,0)
            else:
                h = surface.get_height()
                if loc == "topLeft":
                    location = (0,(sh-h)/2)
                elif loc == "topRight":
                    location = (sw,(sh-h)/2)
                elif loc == "bottomLeft":
                    location = (0, sh + (sh-h)/2)
                elif loc == "bottomRight":
                    location = (sw, sh +(sh-h)/2)
                #location = (0, (sh-h)/2)
        

        self.images_to_draw.append([surface, location])
        

    def drawImages(self):
        for image in self.images_to_draw:
            self.screen.blit(image[0], image[1])
        self.images_to_draw = []

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()

        self.screen.fill((0, 0, 0))

        self.drawImages()

        pygame.display.flip()

        self.clock.tick(60)

    def close(self):
        pygame.quit()
        sys.exit()
