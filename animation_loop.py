import pygame
import neat
import os
import math

# Screen dimensions
WIDTH, HEIGHT = 900, 600
# Colors
WHITE = (255, 255, 255)
# Crayola 8-pack colors (approximate RGB values)
RED = (237, 41, 57)       # Crayola Red
ORANGE = (255, 126, 0)     # Crayola Orange
YELLOW = (252, 233, 79)    # Crayola Yellow
GREEN = (76, 187, 23)      # Crayola Green
CRAYOLA_BLUE = (0, 117, 201)      # Crayola CRAYOLA_BLUE
VIOLET = (114, 62, 163)   # Crayola Violet (or Purple)
BROWN = (150, 78, 45)     # Crayola Brown
BLACK = (0, 0, 0)         # Crayola Black

# Road parameters
AMPLITUDE = 100
FREQUENCY = 0.02
SHIFT_AMOUNT = 5

# Car parameters
CAR_RADIUS = 10
CAR_X = WIDTH // 2 #Chase car is 1/2 of the screen away
TARGET_CAR_OFFSET = WIDTH // 4 #Target car is 1/4 of the screen away

class Road:
    def __init__(self, amplitude, frequency, road_width=WIDTH):
        self.amplitude = amplitude
        self.frequency = frequency
        self.center_points = []  # Points for the center line
        self.top_points = []  # Points for the top edge
        self.bottom_points = []  # Points for the bottom edge
        #
        self.x_offset = 0  # To track the current x-position of the road
        self.road_width = road_width
        self.path_width = HEIGHT // 3
        
        self.generate_initial_road()

    def generate_initial_road(self):
        """Generates points for the center, top, and bottom lines without premature wrapping."""
        self.center_points = []
        self.top_points = []
        self.bottom_points = []

        # Generate road points with sine wave displacement
        for x in range(0, WIDTH + self.road_width * 2, 5):  # Cover initial visible width and extra padding
            center_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * x)

            self.center_points.append((x, center_y))
            self.top_points.append((x, center_y - self.path_width // 2))
            self.bottom_points.append((x, center_y + self.path_width // 2))

    def draw(self, surface):
        """Draws the three road lines."""
        self.draw_line(surface, self.center_points, 3, RED)
        self.draw_line(surface, self.top_points, 2, WHITE)
        self.draw_line(surface, self.bottom_points, 2, GREEN)

    def draw_line(self, surface, points, width, color):
        """Draws the road line given."""
        for i in range(len(points) - 1):  # Use 'points' instead of 'self.points'
            x1 = points[i][0] - self.x_offset  # Apply the offset here
            y1 = points[i][1]
            x2 = points[i + 1][0] - self.x_offset  # Apply the offset here
            y2 = points[i + 1][1]
            if 0 <= x1 <= self.road_width or 0 <= x2 <= self.road_width:  # Only draw lines that are on screen
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)

    def shift(self, shift_amount):
        """Shift all road lines and dynamically add/remove points."""
        self.x_offset += shift_amount

        self.shift_line(self.center_points)
        self.shift_line(self.top_points)
        self.shift_line(self.bottom_points)

    def shift_line(self, points):
        """Shift a single line of points and add/remove points as needed."""
        # Remove points that are off-screen to the left
        while points and points[0][0] < self.x_offset - 10:
            points.pop(0)

        # Add new points to the right to maintain continuity
        while points[-1][0] - self.x_offset < WIDTH + 10:
            last_x = points[-1][0]
            new_x = last_x + 5

            # Use the raw new_x for sine calculations directly
            new_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * new_x)

            # Adjust y for the specific point list
            if points is self.center_points:
                pass  # Center points use the base sine wave
            elif points is self.top_points:
                new_y -= self.path_width // 2
            elif points is self.bottom_points:
                new_y += self.path_width // 2
            else:
                new_y = 0
                print("Error: points list not recognized")

            points.append((new_x, new_y))
            # print(f"last_x = {last_x}, new_x = {new_x}, new_y = {new_y}")

    def get_y_at_x(self, x):
        """Returns the y-value of the sine wave at the given x."""
        for i in range(len(self.center_points) -1):
            if self.center_points[i][0] <= x <= self.center_points[i+1][0]:
                x1 = self.center_points[i][0]
                y1 = self.center_points[i][1]
                x2 = self.center_points[i+1][0]
                y2 = self.center_points[i+1][1]
                slope = (y2-y1)/(x2-x1)
                return y1 + slope*(x - x1)
        return None
class TargetCar: #New target car class
    def __init__(self, x, radius, color):
        self.x = x
        self.radius = radius
        self.y = 0
        self.color = color

    def update(self, road, x_offset):
        road_x = self.x + x_offset
        self.y = road.get_y_at_x(road_x)
        if self.y is None:
            self.y = HEIGHT // 2

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# Initialize Pygame
pygame.init()

#
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Sine Road with Car")

# Create a road object
road = Road(AMPLITUDE, FREQUENCY)
target_car = TargetCar(CAR_X + TARGET_CAR_OFFSET, CAR_RADIUS, CRAYOLA_BLUE)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Shift the road
    road.shift(SHIFT_AMOUNT)

    target_car.update(road, road.x_offset)  # Update the target car position

    # Clear the screen
    SCREEN.fill(BLACK)

    # Draw the road, car, and target car
    road.draw(SCREEN)
    target_car.draw(SCREEN)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

# Quit Pygame
pygame.quit()
sys.exit()
