import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Sine Road with Car")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Road parameters
AMPLITUDE = 100
FREQUENCY = 0.02
SHIFT_AMOUNT = 5

# Car parameters
CAR_RADIUS = 10
CAR_X = WIDTH // 2

class Road:
    def __init__(self, amplitude, frequency):
        self.amplitude = amplitude
        self.frequency = frequency
        self.points = []
        self.x_offset = 0  # To track the current x-position of the road
        self.generate_initial_road()

    def generate_initial_road(self):
        """Generate enough points to fill the screen initially."""
        self.points = []
        for x in range(0, WIDTH * 2, 5):  # Start with enough points to fill screen twice
            y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * x)
            self.points.append((x, y))

    def shift(self, shift_amount):
        """Shift the road and dynamically add/remove points."""
        self.x_offset += shift_amount  # Update the offset

        # Remove points that are off-screen to the left
        while self.points and self.points[0][0] < self.x_offset - 10:  # Add a small buffer
            self.points.pop(0)

        # Add new points to the right to maintain continuity
        while self.points[-1][0] - self.x_offset < WIDTH + 10:  # Add a small buffer
            last_x = self.points[-1][0]  # Get the last x from the points list
            new_x = last_x + 5
            new_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * new_x)
            self.points.append((new_x, new_y))  # Append with the correct absolute x


    def get_y_at_x(self, x):
        """Returns the y-value of the sine wave at the given x."""
        for i in range(len(self.points) -1):
            if self.points[i][0] <= x <= self.points[i+1][0]:
                x1 = self.points[i][0]
                y1 = self.points[i][1]
                x2 = self.points[i+1][0]
                y2 = self.points[i+1][1]
                slope = (y2-y1)/(x2-x1)
                return y1 + slope*(x - x1)
        return None

    def draw(self, surface):
        # print(f"points = {self.points}")
        for i in range(len(self.points) - 1):
            x1 = self.points[i][0] - self.x_offset  # Apply the offset here
            y1 = self.points[i][1]
            x2 = self.points[i+1][0] - self.x_offset  # Apply the offset here
            y2 = self.points[i+1][1]
            if 0 <= x1 <= WIDTH or 0 <= x2 <= WIDTH: #Only draw lines that are on screen
                pygame.draw.line(surface, WHITE, (x1, y1), (x2, y2), 3)

class Car:
    def __init__(self, x, radius):
        self.x = x
        self.radius = radius
        self.y = 0  # Initialize y

    def update(self, road, x_offset):
        """Updates the car's y-position based on the road."""
        road_x = self.x + x_offset #Get the x value on the road
        self.y = road.get_y_at_x(road_x)
        if self.y is None:
            self.y = HEIGHT // 2

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

# Create road and car
road = Road(AMPLITUDE, FREQUENCY)
car = Car(CAR_X, CAR_RADIUS)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Shift the road
    road.shift(SHIFT_AMOUNT)

    car.update(road, road.x_offset)

    # Clear the screen
    SCREEN.fill(BLACK)

    # Draw the road
    road.draw(SCREEN)
    car.draw(SCREEN)

    # Update the display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
