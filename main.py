# /usr/bin/env python2.7

import pygame, sys, math, random
from pygame.locals import *
import colorDict, Algorithms

TILESIZE = 6
FPS = 120
NUM_COL = 160
NUM_ROW = 120
WINWIDTH = NUM_COL*TILESIZE
WINHEIGHT = NUM_ROW*TILESIZE
DRAW_PATH = True
# Setup
pygame.init()
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

class Node(object):
    def __init__(self, x, y, cost=1, reachable=True):
        self.x = x
        self.y = y
        self.cost = cost
        self.status = "Unexplored"
        self.type = '1'
        self.state = "Open"

    def cycle_state(self):
        if self.state == 'Open':
            self.state = 'Difficult'
            self.cost = 5
        elif self.state == 'Difficult':
            self.state = 'Wall'
            self.cost = 0
        elif self.state == 'Wall':
            self.state = 'Open'
            self.cost = 1


class Graph(object):
    def __init__(self):
        self.nodes = {}
        for x in range(NUM_COL):
            for y in range(NUM_ROW):
                self.nodes[(x, y)] = Node(x, y)

        self.num = random.randint(0,3)
        if self.num == 0:
            self.start_x = random.randint(0,NUM_COL-1)
            self.start_y = random.randint(0,19)
        elif self.num == 1:
            self.start_x = random.randint(0,NUM_COL-1)
            self.start_y = random.randint(99,NUM_ROW-1)
        elif self.num == 2: 
            self.start_x = random.randint(0,19)
            self.start_y = random.randint(0,NUM_ROW-1)
        elif self.num == 3:
            self.start_x = random.randint(139,NUM_COL-1)
            self.start_y = random.randint(0,NUM_ROW-1)
        
        
        while(True):
            self.goal_x = random.randint(0,NUM_COL-1)
            self.goal_y = random.randint(0,NUM_ROW-1)
            self.dist = math.hypot(self.goal_x - self.start_x, self.goal_y - self.start_y) 
            if self.dist >= 100:
                break

        print self.start_x,self.start_y,self.goal_x,self.goal_y
        self.start_node = self.nodes[(self.start_x, self.start_y)]
        self.goal_node = self.nodes[(self.goal_x, self.goal_y)]

        self.change_algorithm('Breadth First Search')


    def change_algorithm(self, new_algorithm_name):
        self.current_algorithm = new_algorithm_name
        self.algorithm = Algorithms.algorithm_dict[new_algorithm_name](self.start_node, self.goal_node)
        self.reset()

    def update(self, gameStateObj):
        if gameStateObj['current_algorithm'] != self.current_algorithm:
            self.change_algorithm(gameStateObj['current_algorithm'])
        if self.update_flag:
            self.update_flag = self.algorithm.update(self)
        #self.update_flag = False

    def hard_traverse_generation(self):
        self.coordinates = {}

        for x in range(8):
            self.x = random.randint(0,NUM_COL-1)
            self.y = random.randint(0,NUM_ROW-1)
    
            if (self.x,self.y) not in self.coordinates:
                self.coordinates[(self.x,self.y)] = (self.x,self.y)

        for (x,y) in self.coordinates:
            self.top_left_x = x-16
            self.top_left_y = y-16

            for x in range(31): 
                self.top_left_x += 1
                
                for y in range(31):
                    self.top_left_y += 1
                    
                    if (self.top_left_x,self.top_left_y) in self.nodes:
                        self.fifty_fifty = random.randint(0,1)

                        if self.fifty_fifty == 0:

                            self.nodes[(self.top_left_x,self.top_left_y)].cost = 2
                            self.nodes[(self.top_left_x,self.top_left_y)].type = 2

                self.top_left_y = self.top_left_y-31

    def check_collision(self, x, y):
        if self.nodes[(self.x,self.y)].cost == 3:
            return True
        else:
            return False

    # def go_left(self, highway = []):
    #     x,y = highway[-1]
    #     print x,y

    #     for i in range(20):
    #         if self.check_collision(self.x-i,self.y):
    #             return False
    #         else:
    #             self.highway += [(self.x-i,self.y)]

    # def go_right(self,highway = []):
    #     x,y = highway[-1]
    #     print x,y

    #     for i in range(20):
    #         if self.check_collision(self.x+i,self.y):
    #             return False
    #         else:
    #             self.highway += [(self.x+i,self.y)]

    # def go_up(self, highway = []):
    #     x,y = highway[-1]
    #     print x,y
    #     for i in range(20):
    #         if self.check_collision(self.x,self.y-i):
    #             return False
    #         else:
    #             self.highway += [(self.x,self.y-i)]

    # def go_down(self, highway = []):
    #     x,y = highway[-1]
    #     print x,y
    #     for i in range(20):
    #         if self.check_collision(self.x,self.y+i):
    #             return False
    #         else:
    #             self.highway += [(self.x,self.y+i)]

    def random_border_coordinates(self,borders = {}):
        for i in range(4):

            self.num = random.randint(0,3)
            if self.num == 0:
                self.x = 0
                self.y = random.randint(1,NUM_ROW-2)
            elif self.num == 1:
                self.x = random.randint(1,NUM_COL-2)
                self.y = 0
            elif self.num == 2: 
                self.x = 159
                self.y = random.randint(1,NUM_ROW-2)
            elif self.num == 3:
                self.x = random.randint(1,NUM_COL-2)
                self.y = 119

            if (self.x,self.y) not in self.borders:
                self.borders[(self.x,self.y)] = (self.x,self.y)


    def highway_generation(self):
        self.borders = {}

        for i in range(4):

            self.num = random.randint(0,3)
            if self.num == 0:
                self.x = 0
                self.y = random.randint(1,NUM_ROW-2)
            elif self.num == 1:
                self.x = random.randint(1,NUM_COL-2)
                self.y = 0
            elif self.num == 2: 
                self.x = 159
                self.y = random.randint(1,NUM_ROW-2)
            elif self.num == 3:
                self.x = random.randint(1,NUM_COL-2)
                self.y = 119

            if (self.x,self.y) not in self.borders:
                self.borders[(self.x,self.y)] = (self.x,self.y)

        # idea: always keep the the starting coordinate in the list and 
        #  if need to start deleteing everython from the list except the 
        # first value aka starting coordinate
        for x,y in self.borders:
            self.highway = []
            self.highway.insert(0,(x,y))

            direction = None
            if x == 0:
                self.direction = 'right'
                for i in range(1,20):
                    self.highway += [(x+i,y)]
                # self.go_right(self.highway)
            elif x == 159:
                self.direction = 'left'
                for i in range(1,20):
                    self.highway += [(x-i,y)]
                # self.go_left(self.highway)
            elif y == 0:
                self.direction = 'down'
                for i in range(1,20):
                    self.highway += [(x,y+i)]
                # self.go_down(self.highway)
            elif y == 119: 
                self.direction = 'up'
                for i in range(1,20):
                    self.highway += [(x,y-i)]
                # self.go_up(self.highway)
            
            # put a while loop   
            # checking for true or false and what can switch it to false
            # first check if it has reached a boundary block and when
            # it has needs to check if the list is also greater than or 
            # to 100

            x,y = self.highway[-1]
          
            if random.random() > .2:
                if self.direction == 'right':
                    for i in range(20):
                        self.highway += [(x+i,y)]
                elif self.direction == 'left':
                    for i in range(20):
                        self.highway += [(x-i,y)]
                elif self.direction == 'down':
                    for i in range(20):
                        self.highway += [(x,y+i)]
                elif self.direction == 'up':
                    for i in range(20):
                        self.highway += [(x,y-i)]



            #     # contiinue moving the same direction
            #     # pop the last value of the highway list, chec the 
            #     # the highway is going and contiue in that direction
            # else 
            #     # move perpendicular 
            #     # check direction to determine what perpendicular direction
            #     # to go and then update the new direction of the highway
            #     if random()

            for x,y in self.highway:
                self.nodes[(x,y)].type = 'a'
        

    def draw(self, surf, gameStateObj):
        
        self.hard_traverse_generation()
        # self.highway_generation()
        surf.fill(colorDict.colorDict['white'])
        for position, node in self.nodes.iteritems():
            imageRect = pygame.Rect(node.x*TILESIZE, node.y*TILESIZE, 6, 6)
          
            # If not reachable, fill with dark_gray:
            if node.type == 0:
                pygame.draw.rect(surf, colorDict.colorDict['black'], imageRect)
            # If cost is greater than one, fill with dithered surf
            if node.type == 2:
                 pygame.draw.rect(surf, colorDict.colorDict['dark_gray'], imageRect)
            if node.type == 'a':
                 pygame.draw.rect(surf, colorDict.colorDict['purple'], imageRect)
            # If start, fill with green
            if node is self.start_node:
                pygame.draw.rect(surf, colorDict.colorDict['dark_green'], imageRect)
            # If goal, fill with red
            if node is self.goal_node:
                pygame.draw.rect(surf, colorDict.colorDict['red'], imageRect)
            # Draw outline
            pygame.draw.rect(surf, colorDict.colorDict['light_gray'], imageRect, 1)

        if DRAW_PATH:
            if isinstance(self.algorithm, Algorithms.Bidirectional):
                for forward_path in self.algorithm.forward_path:
                    for index in range(len(forward_path) - 1):
                        current = forward_path[index]
                        next = forward_path[index + 1]
                        old_pos = current.x*TILESIZE + TILESIZE/2 - 2, current.y*TILESIZE + TILESIZE/2 - 2
                        new_pos = next.x*TILESIZE + TILESIZE/2 - 2, next.y*TILESIZE + TILESIZE/2 - 2
                        pygame.draw.line(surf, colorDict.colorDict['dark_purple'], old_pos, new_pos, 4)
                for backward_path in self.algorithm.backward_path:
                    for index in range(len(backward_path) - 1):
                        current = backward_path[index]
                        next = backward_path[index + 1]
                        old_pos = current.x*TILESIZE + TILESIZE/2 - 2, current.y*TILESIZE + TILESIZE/2 - 2
                        new_pos = next.x*TILESIZE + TILESIZE/2 - 2, next.y*TILESIZE + TILESIZE/2 - 2
                        pygame.draw.line(surf, colorDict.colorDict['dark_purple'], old_pos, new_pos, 4)

            elif self.algorithm.came_from and self.goal_node in self.algorithm.came_from:
                current = self.goal_node
                path = [current]
                while current is not self.start_node:
                    old_pos = current.x*TILESIZE + TILESIZE/2 - 2, current.y*TILESIZE + TILESIZE/2 - 2
                    current = self.algorithm.came_from[current]
                    new_pos = current.x*TILESIZE + TILESIZE/2 - 2, current.y*TILESIZE + TILESIZE/2 - 2
                    # Draw line
                    pygame.draw.line(surf, colorDict.colorDict['dark_purple'], old_pos, new_pos, 4)
                    path.append(current)

    def get_neighbors(self, node):
        adj_positions = {(node.x, node.y - 1), (node.x, node.y + 1), (node.x - 1, node.y), (node.x + 1, node.y)}
        neighbors = set()
        for adj_position in adj_positions:
            if adj_position in self.nodes and self.nodes[adj_position].cost:
                neighbors.add(self.nodes[adj_position])
        return neighbors

    def reset(self):
        for pos, node in self.nodes.iteritems():
            node.status = "Unexplored"
        self.algorithm.reset()
        self.update_flag = False

    def start(self):
        self.update_flag = True

    def get_node_at_pos(self, pos):
        pos_x = pos[0]/TILESIZE
        pos_y = pos[1]/TILESIZE

        if (pos_x, pos_y) in self.nodes:
            return self.nodes[(pos_x, pos_y)]
        else:
            return None


# === MAIN ===================================================================
def main():
    # Initial Setup
    gameStateObj = {'draw_arrows': False,
                    'draw_numbers': False,
                    'current_algorithm': 'Breadth First Search',
                    'lock_to_ui': False}
    my_graph = Graph()
    my_graph.draw(DISPLAYSURF, gameStateObj)

    # if start_pressed:
    my_graph.start()

    # Update
    my_graph.update(gameStateObj)
    # Draw 

    pygame.display.update()
    FPSCLOCK.tick(FPS)
    # Main game loop
    while(True):
        eventList = [] # Clear event list
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            eventList.append(event)


        

# === TERMINATE ==============================================================
def terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()