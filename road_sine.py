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
FREQUENCY = 0.01
ROAD_WIDTH = 2000  # Width of the road surface
SHIFT_AMOUNT = 5
X_OFFSET = 0

class Road:
    def __init__(self, amplitude, frequency, road_width):
        self.amplitude = amplitude
        self.frequency = frequency
        self.road_width = road_width
        self.points = []
        self.generate_sine_road()

    def generate_sine_road(self):
        self.points = []
        for x in range(0, self.road_width + 1, 5):  # Adjust step for road detail
            y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * x)
            self.points.append((x, y))

    def shift(self, shift_amount):
        for i in range(len(self.points)):
          self.points[i] = (self.points[i][0]-shift_amount, self.points[i][1])
        if self.points[0][0] < -100: #Remove points that are off screen
            self.points.pop(0)
            self.points.append((self.points[-1][0]+5, HEIGHT // 2 + self.amplitude * math.sin(self.frequency * (self.points[-1][0]+5))))



# Create road and surface
road = Road(AMPLITUDE, FREQUENCY, ROAD_WIDTH)
road_surface = pygame.Surface((ROAD_WIDTH, HEIGHT))

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Shift the road surface
    X_OFFSET -= SHIFT_AMOUNT
    road.shift(SHIFT_AMOUNT)

    #Redraw the road
    road_surface.fill(BLACK)
    for i in range(len(road.points) - 1):
        pygame.draw.line(road_surface, WHITE, road.points[i], road.points[i+1], 3)

    # Blit the visible portion of the road surface
    SCREEN.blit(road_surface, (X_OFFSET, 0), (-X_OFFSET, 0, WIDTH, HEIGHT))

    # Keep the offset within the road surface bounds for looping
    if X_OFFSET <= -ROAD_WIDTH:
        X_OFFSET = 0

    pygame.display.flip()
    clock.tick(30)

pygame.quit()