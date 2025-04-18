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

        self.images_to_draw = []

        self.clock = pygame.time.Clock()

    def blit(self, surface, location, type = "path", resize=False):
        if type == "path":
            surface = pygame.image.load(surface)

        if resize:
            w = surface.get_width()
            h = surface.get_height()

            width_scale = SCREEN_WIDTH / w
            height_scale = SCREEN_HEIGHT / h
            scale = min(width_scale, height_scale)

            print(scale)
            surface = pygame.transform.scale(surface, (w * scale, h * scale))
            
            if width_scale > height_scale:
                w = surface.get_width()
                location = ((SCREEN_WIDTH-w)/2,0)
            else:
                h = surface.get_height()
                location = (0, (SCREEN_HEIGHT-h)/2)

        self.images_to_draw.append([surface, location])
        

    def drawImages(self):
        for image in self.images_to_draw:
            self.screen.blit(image[0], image[1])
        self.images_to_draw = []

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        self.screen.fill((0, 0, 0))

        self.drawImages()

        pygame.display.flip()

        self.clock.tick(60)

    def close(self):
        pygame.quit()
        sys.exit()
