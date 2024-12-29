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
CRAYOLA_BLUE = (31, 117, 254) #Define crayola blue

# Road parameters
AMPLITUDE = 100
FREQUENCY = 0.02
SHIFT_AMOUNT = 5

# Car parameters
CAR_RADIUS = 10
CAR_X = WIDTH // 2 #Chase car is 1/2 of the screen away
TARGET_CAR_OFFSET = WIDTH // 4 #Target car is 1/4 of the screen away

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

class Car: #Red car
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

    def get_radar_data(self, target_car):
        """Calculates distance and angle to the target car."""
        dx = target_car.x - self.x
        dy = target_car.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx) #Returns the angle in radians
        return distance, angle
    def update(self, road, x_offset):
        """Updates the car's y-position based on the road."""
        road_x = self.x + x_offset #Get the x value on the road
        self.y = road.get_y_at_x(road_x)
        if self.y is None:
            self.y = HEIGHT // 2

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
# Create road, car, and target car
road = Road(AMPLITUDE, FREQUENCY) #Create the sine road
car = Car(CAR_X, CAR_RADIUS) #Create the pursuit car
target_car = TargetCar(CAR_X + TARGET_CAR_OFFSET, CAR_RADIUS, CRAYOLA_BLUE) #Create the target car

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
    target_car.update(road, road.x_offset) #Update the target car position
    distance, angle = car.get_radar_data(target_car)

    # Clear the screen
    SCREEN.fill(BLACK)

    # Draw the road, car, and target car
    road.draw(SCREEN)
    car.draw(SCREEN)
    target_car.draw(SCREEN)

    # Draw the radar line
    pygame.draw.line(SCREEN, RED, (car.x, car.y), (target_car.x, target_car.y), 2)

    # Update the display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
