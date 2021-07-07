import pygame
from pygame.sprite import Sprite


class TieFighter(Sprite):
    """A class to represent a single TIE Fighter in the fleet."""

    def __init__(self, ai_settings, screen):
        """Initialize the TIE Fighter and set its starting position."""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Load the TIE Fighter image and set its rect attribute.
        self.image = pygame.image.load('data/images/fighter.bmp')
        self.rect = self.image.get_rect()

        # Start each new TIE Fighter near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the TIE Fighter's exact position.
        self.x = float(self.rect.x)

    def blitme(self):
        """Draw the TIE Fighter at its current location."""
        self.screen.blit(self.image, self.rect)

    def update(self):
        """Move the TIE Fighter right or left."""
        self.x += self.ai_settings.fighter_speed_factor*self.ai_settings.fleet_direction
        self.rect.x = self.x

    def check_edges(self):
        """Return True if TIE Fighter is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True
