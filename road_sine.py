import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Sine Road")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Road parameters
AMPLITUDE = 100
FREQUENCY = 0.02  # Adjusted for better visual scrolling
ROAD_WIDTH = 2000  # Total width of the road (larger than the visible area)
SHIFT_AMOUNT = 5  # Pixels per frame

class Road:
    def __init__(self, amplitude, frequency, road_width):
        self.amplitude = amplitude
        self.frequency = frequency
        self.road_width = road_width
        self.points = []
        self.generate_sine_road()

    def generate_sine_road(self):
        """Generate the initial sine wave points for the road."""
        self.points = []
        for x in range(0, self.road_width + 1, 5):  # Increment determines detail
            y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * x)
            self.points.append((x, y))

    def shift(self, shift_amount):
        """Shift the road points and append new points to maintain continuity."""
        # Shift existing points
        self.points = [(x - shift_amount, y) for x, y in self.points]

        # Remove points that have moved off-screen
        while self.points and self.points[0][0] < -5:
            self.points.pop(0)

        # Add new points to the end of the road
        while self.points[-1][0] < self.road_width:
            last_x = self.points[-1][0]
            new_x = last_x + 5
            new_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * new_x)
            self.points.append((new_x, new_y))

# Create road and surface
road = Road(AMPLITUDE, FREQUENCY, ROAD_WIDTH)

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Shift the road surface
    road.shift(SHIFT_AMOUNT)

    # Clear the screen
    SCREEN.fill(BLACK)

    # Draw the road
    for i in range(len(road.points) - 1):
        pygame.draw.line(SCREEN, WHITE, road.points[i], road.points[i + 1], 3)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

    print(road.points)
pygame.quit()
