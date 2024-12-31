import pygame
import neat
import os
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Sine Road with Car")

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
        self.generate_initial_road()


    def generate_initial_road(self):
        """Generates points for the center, top, and bottom lines."""
        self.center_points = []
        self.top_points = []
        self.bottom_points = []
        for x in range(0, self.road_width * 2, 5):
            center_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * x)
            self.center_points.append((x, center_y))
            self.top_points.append((x, center_y - self.road_width // 2))
            self.bottom_points.append((x, center_y + self.road_width // 2))

    def draw(self, surface):
        """Draws the three road lines."""
        self.draw_line(surface, self.center_points, 3, WHITE)
        self.draw_line(surface, self.top_points, 2, WHITE)
        self.draw_line(surface, self.bottom_points, 2, WHITE)

    def draw_line(self, surface, points, width, color):
        """Draws the road line given."""
        for i in range(len(self.points) - 1):
            x1 = self.points[i][0] - self.x_offset  # Apply the offset here
            y1 = self.points[i][1]
            x2 = self.points[i+1][0] - self.x_offset  # Apply the offset here
            y2 = self.points[i+1][1]
            if 0 <= x1 <= self.road_width or 0 <= x2 <= self.road_width: #Only draw lines that are on screen
                pygame.draw.line(surface, WHITE, (x1, y1), (x2, y2), 3)

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
            if points is self.center_points:
                new_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * new_x)
            elif points is self.top_points:
                new_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * new_x) - self.road_width // 2
            elif points is self.bottom_points:
                new_y = HEIGHT // 2 + self.amplitude * math.sin(self.frequency * new_x) + self.road_width // 2
            else:
                new_y = 0
                print("Error points list not recognized")
            points.append((new_x, new_y))


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

class Car: #Red car
    def __init__(self, x, radius):
        self.x = x
        self.dx = 0
        self.radius = radius
        self.y = HEIGHT // 2 # Initialize y
        self.dy = 0
        self.velocity = 5  # New attribute to track vertical speed
        self.alive = True
        self.angle = 0
        self.distance = 0
        self.radar_data = []

    def update(self, action, road, x_offset):
        """Update the car's y-position based on NEAT output."""
        if not self.alive:
            return

        if len(action) >= 3:
            up = action[0]
            down = action[1]
            hold = action[2]

            if up > down and up > hold:
                self.y -= 5  # Move up for one frame
            elif down > up and down > hold:
                self.y += 5  # Move down for one frame
            # Hold does not change the y value

        road_x = self.x + x_offset
        road_y = road.get_y_at_x(road_x)

        if road_y is None or abs(self.y - road_y) > AMPLITUDE * 2.5 or self.y < 0 or self.y > HEIGHT:
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            pygame.draw.circle(screen, CRAYOLA_BLUE, (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

    def get_radar_data(self, road, num_beams=12):
        """Calculates distance and angle to the road edges."""
        self.radar_data = []
        for i in range(num_beams):
            angle = (i / num_beams) * 2 * math.pi

            ray_length = 0
            ray_x = self.x
            ray_y = self.y
            while ray_length < 200:
                ray_x += math.cos(angle)
                ray_y += math.sin(angle)
                ray_length += 1

                # Check intersection with top and bottom points
                intersect_top = self.find_intersection(self.x, self.y, ray_x, ray_y, road.top_points, road.x_offset)
                intersect_bottom = self.find_intersection(self.x, self.y, ray_x, ray_y, road.bottom_points,
                                                          road.x_offset)

                if intersect_top is not None:
                    dist = math.sqrt((intersect_top[0] - self.x) ** 2 + (intersect_top[1] - self.y) ** 2)
                    self.radar_data.append((dist, angle))
                    ray_length = 200  # End the ray cast
                    break  # Stop checking points for this ray

                if intersect_bottom is not None:
                    dist = math.sqrt((intersect_bottom[0] - self.x) ** 2 + (intersect_bottom[1] - self.y) ** 2)
                    self.radar_data.append((dist, angle))
                    ray_length = 200  # End the ray cast
                    break  # Stop checking points for this ray

        return self.radar_data

    def find_intersection(self, x1, y1, x2, y2, points, x_offset):
        for i in range(len(points) - 1):
            x3 = points[i][0] - x_offset
            y3 = points[i][1]
            x4 = points[i + 1][0] - x_offset
            y4 = points[i + 1][1]

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

# Create road, car, and target car and NEAT inputs


# Main NEAT evaluation function
def eval_genomes(genomes, config):

    road = Road(AMPLITUDE, FREQUENCY)
    target_car = TargetCar(CAR_X + TARGET_CAR_OFFSET, CAR_RADIUS, CRAYOLA_BLUE)

    cars = []
    nets = []
    ge = []

    # Initialize cars, genomes, and networks
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        car = Car(CAR_X, CAR_RADIUS)
        car.get_radar_data(road)
        cars.append(car)
        ge.append(genome)

    run = True
    first_pass = False
    clock = pygame.time.Clock()

    while run and any(car.alive for car in cars):
        # Shift the road
        road.shift(SHIFT_AMOUNT)

        target_car.update(road, road.x_offset)  # Update the target car position

        for i, car in enumerate(cars):
            if not car.alive:
                continue
            else:
                car.get_radar_data(road) #Gets boundary vector angle and magnitude


        # Clear the screen
        SCREEN.fill(BLACK)

        # Draw the road, car, and target car
        road.draw(SCREEN)
        target_car.draw(SCREEN)

        # Update each car
        for i, car in enumerate(cars):
            if not car.alive:
                continue

            # Inputs for the NEAT network
            distance_angle_list = car.radar_data
            inputs = []
            #Now add both the distance and angle to the inputs list in a single operation.
            for distance, angle in distance_angle_list:
                inputs.extend([distance, angle])  # Use extend to add both elements

            output = nets[i].activate(tuple(inputs))

            car.update(output,road, road.x_offset)

            # ... inside the game loop in eval_genomes
            y_on_road = road.get_y_at_x(car.x + road.x_offset)
            if y_on_road is not None:
                distance_from_road = abs(car.y - y_on_road)
                if distance_from_road < road.road_width // 2:  # Check if the car is on the road
                    ge[i].fitness += (road.road_width // 2 - distance_from_road)  # Reward being close to the center
                else:
                    ge[i].fitness -= 100
                    running = False
                    break
            else:
                ge[i].fitness -= 100
                running = False
                break
                # Update fitness
            # Draw the car
            car.draw(SCREEN)
            pygame.draw.line(SCREEN, RED, (car.x, car.y), (target_car.x, target_car.y), 2)
            # Draw radar beams
            for distance, angle in distance_angle_list:
                end_x = car.x + distance * math.cos(angle)
                end_y = car.y + distance * math.sin(angle)
                pygame.draw.line(SCREEN, GREEN, (car.x, car.y), (end_x, end_y), 1)

        # Update the display
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()

# Configuration for NEAT
def run_neat(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(eval_genomes, 50)
    print("\nBest genome:\n", winner)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
