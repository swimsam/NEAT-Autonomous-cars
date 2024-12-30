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
        self.dx = 0
        self.radius = radius
        self.y = HEIGHT // 2 # Initialize y
        self.dy = 0
        self.velocity = 5  # New attribute to track vertical speed
        self.alive = True
        self.angle = 0
        self.distance = 0

    def update(self, action, road, x_offset):
        """Update the car's y-position based on NEAT output."""
        if not self.alive:
            return
        # 
        if action[0] > action[1]:
            self.velocity -= 5  # Move up
        elif action[1] > action[0]:
            self.velocity += 5  # Move down

        self.y += self.velocity  # Update position based on velocity

        road_x = self.x + x_offset #Get the x value on the road
        road_y = road.get_y_at_x(road_x)

        if road_y is None or abs(self.y - road_y) > AMPLITUDE*2.5 or self.y < 0 or self.y > HEIGHT:
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            pygame.draw.circle(screen, CRAYOLA_BLUE, (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

    def get_radar_data(self, target_car):
        """Calculates distance and angle to the target car."""
        self.dx = target_car.x - self.x
        self.dy = target_car.y - self.y
        self.distance = math.sqrt(self.dx ** 2 + self.dy ** 2)
        self.angle = math.atan2(self.dy, self.dx) #Returns the angle in radians
        return self.distance, self.angle

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
        car.get_radar_data(target_car)
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
                car.get_radar_data(target_car) #Gets the target car vector angle and magnitue


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
            car_x_on_road = car.x
            car_y_on_road = road.get_y_at_x(car_x_on_road)
            if car_y_on_road is None:
                car_y_on_road = 0
            distance_to_target_car = car.distance
            angle_to_target_car = car.angle
            # print(f"car_x_on_road = {car_x_on_road}")
            # print(f"car_y_on_road = {car_y_on_road}")
            cars_speed = car.velocity

            distance_to_road = car_y_on_road - car.y

            inputs = [
                angle_to_target_car,  #  angle of vector from car to target car
                distance_to_target_car,  #  length of vector
                distance_to_road,  #  vertical distance between car and road, sims another radar
                cars_speed
            ]

            output = nets[i].activate(inputs)
            car.update(output,road, road.x_offset)

            y_on_road = road.get_y_at_x(car.x + road.x_offset)
            if y_on_road is not None:
                distance_from_road = abs(car.y - y_on_road)
                if distance_from_road < 10:
                    ge[i].fitness += 1
                elif distance_from_road > 10:
                    ge[i].fitness -= 2
                if abs(cars_speed) < 1:
                    ge[i].fitness -= 3
                if car_y_on_road == car.y:
                    ge[i].fitness += 5
                # else:
                #     ge[i].fitness -= distance_from_road / 10
            else:
                ge[i].fitness -= 100
                run = False
                break
             # Update fitness
            ge[i].fitness = distance_to_road
            # print(f"ge[i].fitness += {ge[i].fitness}")
            # Draw the car
            car.draw(SCREEN)
            pygame.draw.line(SCREEN, RED, (car.x, car.y), (target_car.x, target_car.y), 2)

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
