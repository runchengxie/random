import pygame
import random
import heapq

# Screen dimensions
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class SnakeAI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AI Snake Game")
        self.clock = pygame.time.Clock()
        
        # Snake initialization
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.food = self.generate_food()
        
        # Game state
        self.score = 0
        self.game_over = False

    def generate_food(self):
        while True:
            food_pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if food_pos not in self.snake:
                return food_pos

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = [
            (x+1, y), (x-1, y),
            (x, y+1), (x, y-1)
        ]
        # Filter out invalid positions
        return [
            n for n in neighbors 
            if 0 <= n[0] < GRID_WIDTH and 
               0 <= n[1] < GRID_HEIGHT and 
               n not in self.snake[1:]
        ]

    def a_star_search(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current_cost, current = heapq.heappop(frontier)

            if current == goal:
                break

            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Reconstruct path
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def move_snake(self):
        head = self.snake[0]
        
        # Find path to food using A* search
        path = self.a_star_search(head, self.food)
        
        # If path exists, move towards first step
        if path:
            next_pos = path[0]
            self.direction = (next_pos[0] - head[0], next_pos[1] - head[1])
        
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check game over conditions
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, 
                             (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, 
                              GRID_SIZE-1, GRID_SIZE-1))
        
        # Draw food
        pygame.draw.rect(self.screen, RED, 
                         (self.food[0]*GRID_SIZE, self.food[1]*GRID_SIZE, 
                          GRID_SIZE-1, GRID_SIZE-1))
        
        pygame.display.flip()

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            self.move_snake()
            self.draw()
            
            # Control game speed
            self.clock.tick(10)  # 10 FPS for visibility of AI movement

        pygame.quit()

if __name__ == "__main__":
    game = SnakeAI()
    game.run()
