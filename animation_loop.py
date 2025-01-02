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

class Car:  # Red car
    def __init__(self, x, radius):
        self.x = x
        self.y = HEIGHT // 2  # Initialize y
        self.dx = 0
        self.dy = 0  # Future use
        self.radius = radius
        self.velocity = 5
        self.alive = True
        self.angle = 0
        self.distance = 0
        self.radar_data = []
        self.show_radar = True  # Flag to control radar beam visibility

    def update_test(self, road, x_offset):
        road_x = self.x + x_offset
        self.y = road.get_y_at_x(road_x)
        if self.y is None:
            self.y = HEIGHT // 2

    def update(self, action, road, x_offset):
        if not self.alive:
            return

        if len(action) >= 3:
            up, down, hold = action
            if up > down and up > hold:
                self.y -= self.velocity
            elif down > up and down > hold:
                self.y += self.velocity

        road_x = self.x + x_offset
        road_y = road.get_y_at_x(road_x)

        if road_y is None:
            self.alive = False
            print("Car went off-road: No road_y found.")
        elif abs(self.y - road_y) > AMPLITUDE * 2.5:
            self.alive = False
            print(f"Car too far from road: y={self.y}, road_y={road_y}")
        elif self.y < 0 or self.y > HEIGHT:
            self.alive = False
            print(f"Car out of bounds: y={self.y}")

    def draw(self, screen):
        color = CRAYOLA_BLUE if not self.alive else RED
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)

        if self.show_radar:
            self.draw_radar(screen)


    def get_radar_data(self, road, num_beams=10):
        """Calculates distance and angle to the road edges and stores radar data."""
        self.radar_data = []
        for i in range(num_beams):
            angle = (i / num_beams) * 2 * math.pi
            ray_length = 0
            ray_x, ray_y = self.x, self.y

            while ray_length < 200:  # Maximum range
                ray_x += math.cos(angle)
                ray_y += math.sin(angle)
                ray_length += 1

                # Check intersections
                intersect_top = self.find_intersection(self.x, self.y, ray_x, ray_y, road.top_points, road.x_offset)
                intersect_bottom = self.find_intersection(self.x, self.y, ray_x, ray_y, road.bottom_points, road.x_offset)

                if intersect_top is not None:
                    dist = math.sqrt((intersect_top[0] - self.x) ** 2 + (intersect_top[1] - self.y) ** 2)
                    self.radar_data.append((angle, dist))
                    break  # Stop checking after the first intersection

                if intersect_bottom is not None:
                    dist = math.sqrt((intersect_bottom[0] - self.x) ** 2 + (intersect_bottom[1] - self.y) ** 2)
                    self.radar_data.append((angle, dist))
                    break

            else:
                # If no intersection, append max range
                self.radar_data.append((angle, 200))

        return self.radar_data

    def draw_radar(self, screen):
        """Visualize the radar beams on the screen."""
        for angle, dist in self.radar_data:
            end_x = self.x + dist * math.cos(angle)
            end_y = self.y + dist * math.sin(angle)
            pygame.draw.line(screen, GREEN, (self.x, self.y), (end_x, end_y), 1)
            pygame.draw.circle(screen, RED, (int(end_x), int(end_y)), 2)  # Mark intersection point

    def find_intersection(self, x1, y1, x2, y2, points, x_offset):
        # Calculate the x-range of interest
        min_x = min(x1, x2) - AMPLITUDE
        max_x = max(x1, x2) + AMPLITUDE

        # Filter points to those within the x-range
        relevant_points = [
            (points[i], points[i + 1])
            for i in range(len(points) - 1)
            if min_x <= points[i][0] - x_offset <= max_x or min_x <= points[i + 1][0] - x_offset <= max_x
        ]

        # Check for intersections only within the narrowed points
        for p1, p2 in relevant_points:
            x3 = p1[0] - x_offset
            y3 = p1[1]
            x4 = p2[0] - x_offset
            y4 = p2[1]

            denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            if denom == 0:
                continue

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom

            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                return x, y

        return None

    def find_intersectionx(self, x1, y1, x2, y2, points, x_offset):
        # Define the maximum x-range for searching based on wavelength and radar angle
        max_x = max(x1, x2)
        min_x = min(x1, x2)

        # Allow a small buffer to account for beam spread
        buffer = 10  # You can adjust this based on the scenario
        search_range = (max(0, min_x - buffer), max_x + buffer)

        # Filter points within the x-range
        filtered_points = [
            points[i] for i in range(len(points) - 1)
            if search_range[0] <= points[i][0] - x_offset <= search_range[1]
        ]

        for i in range(len(filtered_points) - 1):
            x3 = filtered_points[i][0] - x_offset
            y3 = filtered_points[i][1]
            x4 = filtered_points[i + 1][0] - x_offset
            y4 = filtered_points[i + 1][1]

            denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            if denom == 0:
                continue  # Lines are parallel

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom

            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                return x, y

        return None


# Initialize Pygame
pygame.init()

#
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Sine Road with Car")

# Create a road object
road = Road(AMPLITUDE, FREQUENCY)
target_car = TargetCar(CAR_X + TARGET_CAR_OFFSET, CAR_RADIUS, CRAYOLA_BLUE)
car = Car(CAR_X, CAR_RADIUS)
# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Shift the road
    road.shift(SHIFT_AMOUNT)

    target_car.update(road, road.x_offset)  # Update the target car position
    car.update_test(road, road.x_offset)  # Update the target car position
    car.get_radar_data(road)

    # Clear the screen
    SCREEN.fill(BLACK)

    # Draw the road, car, and target car
    road.draw(SCREEN)
    target_car.draw(SCREEN)
    car.draw(SCREEN)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

# Quit Pygame
pygame.quit()
sys.exit()
