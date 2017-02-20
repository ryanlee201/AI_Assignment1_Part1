# /usr/bin/env python2.7
'''
Intro to Artificial Intelligence Project 1
Dean Keinan, Ryan Lee
'''

import pygame, sys, math, random, heapq, os, time
from random import randint
from ast import literal_eval as make_tuple

pygame.init()
font = pygame.font.SysFont("courier new", 15)

TILESIZE = 6  # Drawing dimensions of block
FPS = 120
NUM_COL = 160
NUM_ROW = 120
WINWIDTH = NUM_COL * TILESIZE
WINHEIGHT = NUM_ROW * TILESIZE
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINWIDTH + 200, WINHEIGHT + 34))

# Graph Generation
# Note: Adjusted the representation of the graph to avoid creating a Node object. Instead used internal string
# at coordinate in 2D array to represent cost.

graph = [['open' for y in range(NUM_ROW)] for x in range(NUM_COL)]
pointer_x = 0
pointer_y = 0
goal_x = 1
goal_y = 1


# generate a random Graph
def generateGraph():
    # Hard-to-Traverse Area Generation

    hard_traverse_count = 0
    hard_traverse_nodes = []

    while hard_traverse_count < 8:
        hard_traverse_x = randint(0, NUM_COL - 1)
        hard_traverse_y = randint(0, NUM_ROW - 1)

        if (hard_traverse_x, hard_traverse_y) not in hard_traverse_nodes:
            hard_traverse_nodes.append((hard_traverse_x, hard_traverse_y))
            for x in range(hard_traverse_x - 15, hard_traverse_x + 15):
                if 0 <= x < NUM_COL:
                    for y in range(hard_traverse_y - 15, hard_traverse_y + 15):
                        if 0 <= y < NUM_ROW:
                            if randint(0, 9) < 5:
                                graph[x][y] = 'hard_traverse'
            hard_traverse_count += 1

    # HIGHWAY GENERATION
    highway_count = 0

    while highway_count < 4:
        highway = []
        x = randint(1, NUM_COL - 2)
        y = randint(1, NUM_ROW - 2)

        highway_valid = True  # Flag to let us know if our highway meets length / crossing requirements

        # Starting orientations represented by integers
        # 0 = Up
        # 1 = Right
        # 2 = Down
        # 3 = Left

        starting_orientation = randint(0, 3)
        if starting_orientation == 0:
            y = 0
            direction = 2
        elif starting_orientation == 1:
            x = NUM_COL - 1
            direction = 3
        elif starting_orientation == 2:
            y = NUM_ROW - 1
            direction = 0
        else:
            x = 0
            direction = 1

        highway_length = 0
        step_count = 0

        while True:
            # OOB Check
            if x < 0 or x >= NUM_COL or y < 0 or y >= NUM_ROW:
                break

            # Quit if crossed a highway
            if graph[x][y] == 'highway' or graph[x][y] == 'blocked_highway':
                highway_valid = False
                break
            if (x, y) in highway:
                highway_valid = False
                break

            highway.append((x, y))
            step_count += 1
            highway_length += 1

            if direction == 0:  # Up
                y -= 1
            elif direction == 1:  # Right
                x += 1
            elif direction == 2:  # Down
                y += 1
            else:  # left
                x -= 1

            if step_count >= 20:
                step_count = 0
                if randint(0, 99) > 60:
                    if direction == 0:
                        direction = random.choice([1, 3])
                    elif direction == 1:
                        direction = random.choice([0, 2])
                    elif direction == 2:
                        direction = random.choice([1, 3])
                    else:
                        direction = random.choice([0, 2])

        if highway_length < 100:
            highway_valid = False

        if highway_valid == True:
            for node in highway:
                if graph[node[0]][node[1]] == 'open':
                    graph[node[0]][node[1]] = 'highway'
                else:
                    graph[node[0]][node[1]] = 'blocked_highway'

            highway_count += 1

    # Blocked cells
    WALL_MAX = NUM_COL * NUM_ROW * 0.2
    walls = 0

    while walls < WALL_MAX:
        x = randint(0, NUM_COL - 1)
        y = randint(0, NUM_ROW - 1)
        if graph[x][y] == 'open' or graph[x][y] == 'hard_traverse':
            graph[x][y] = 'blocked'
            walls += 1

    return hard_traverse_nodes


def generate_endpoints():
    # Start
    x = randint(0, 39)
    y = randint(0, 39)
    if x > 20:
        x = NUM_COL - x + 20
    if y > 20:
        y = NUM_ROW - y + 20

    while graph[x][y] == 'highway' or graph[x][y] == 'blocked_highway' or graph[x][y] == 'blocked':
        x = randint(0, 39)
        y = randint(0, 39)
        if x > 20:
            x = NUM_COL - x + 20
        if y > 20:
            y = NUM_ROW - y + 20

    start_x = x
    start_y = y

    # End
    while graph[x][y] == 'highway' or graph[x][y] == 'blocked_highway' or graph[x][y] == 'blocked' or math.sqrt(
                            (x - start_x) ** 2 + (y - start_y) ** 2) < 100:
        x = randint(0, 39)
        y = randint(0, 39)
        if x > 20:
            x = NUM_COL - x + 20
        if y > 20:
            y = NUM_ROW - y + 20

    end_x = x
    end_y = y

    # Return points

    return start_x, start_y, end_x, end_y


def get_neighbors(x, y):
    adj_positions = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y), (x + 1, y), (x - 1, y + 1), (x, y + 1),
                     (x + 1, y + 1)]
    adj_positions[:] = [neighbor for neighbor in adj_positions if
                        neighbor[0] >= 0 and neighbor[1] >= 0 and neighbor[0] < NUM_COL and neighbor[1] < NUM_ROW and
                        graph[neighbor[0]][neighbor[1]] != 'blocked']
    return adj_positions


def get_cost(x_origin, y_origin, x_dest, y_dest):
    cost = 0.0

    if (graph[x_origin][y_origin] == 'blocked_highway' or graph[x_origin][y_origin] == 'hard_traverse') and (
                    graph[x_dest][y_dest] == 'hard_traverse' or graph[x_dest][y_dest] == 'blocked_highway'):
        if (x_origin == x_dest - 1 or x_origin == x_dest + 1) and (y_origin == y_dest - 1 or y_origin == y_dest + 1):
            # Diagonal crossing between blocked highway /hard traverse
            cost = math.sqrt(8)
        else:
            # crossing between blocked highway / hard traverse
            cost = 2

    if (graph[x_origin][y_origin] == 'highway' or graph[x_origin][y_origin] == 'open') and (
                    graph[x_dest][y_dest] == 'highway' or graph[x_dest][y_dest] == 'open'):
        if (x_origin == x_dest - 1 or x_origin == x_dest + 1) and (y_origin == y_dest - 1 or y_origin == y_dest + 1):
            # Diagonal crossing between open and highway cells
            cost = math.sqrt(2)
        else:
            # Crossing between open and highway cells
            cost = 1

    if (graph[x_origin][y_origin] == 'highway' or graph[x_origin][y_origin] == 'open') and (
                    graph[x_dest][y_dest] == 'hard_traverse' or graph[x_dest][y_dest] == 'blocked_highway'):
        if (x_origin == x_dest - 1 or x_origin == x_dest + 1) and (y_origin == y_dest - 1 or y_origin == y_dest + 1):
            # Diagonal crossing between highway/open to blocked_highway/hard_traverse
            cost = (math.sqrt(2) + math.sqrt(8)) / 2
        else:
            # Crossing between highway/open to blocked_highway/hard_traverse
            cost = 1.5

    if (graph[x_origin][y_origin] == 'hard_traverse' or graph[x_origin][y_origin] == 'blocked_highway') and (
                    graph[x_dest][y_dest] == 'open' or graph[x_dest][y_dest] == 'highway'):
        if (x_origin == x_dest - 1 or x_origin == x_dest + 1) and (y_origin == y_dest - 1 or y_origin == y_dest + 1):
            cost = (math.sqrt(2) + math.sqrt(8)) / 2
            # diagonal crossing from hard/blocked_highway to open/highway
        else:
            # crossing from hard/blocked_highway to open/highway
            cost = 1.5

    if (graph[x_origin][y_origin] == 'highway' or graph[x_origin][y_origin] == 'blocked_highway') and (
                    graph[x_dest][y_dest] == 'highway' or graph[x_dest][y_dest] == 'blocked_highway') and (
                ((x_origin == x_dest + 1 or x_origin == y_dest - 1) and y_origin == y_dest) or (
                        (y_origin == y_dest + 1 or y_origin == y_dest - 1) and x_origin == x_dest)):
        cost /= 4
        return cost

    return cost


class Point:
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_parent(self):
        return self.parent


class Queue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(self, startx, starty, goalx, goaly, choice):
    start = (startx, starty)
    goal = (goalx, goaly)
    choice = int(choice)

    if choice == 1:  # manhattan
        heuristic = abs(int(startx) - int(goalx)) + abs(int(starty) - int(goaly))
        heuristic *= (
            1.0 + (0.25 / 160))  # tie-breaker by multiplying the heuristic by (minimum cost)/(max possible path length)
        return heuristic
    if choice == 2:  # euclidean
        heuristic = math.sqrt(((int(startx) - int(goalx)) ** 2) + ((int(starty) - int(goaly)) ** 2))
        heuristic *= (
            1.0 + (0.25 / 160))  # tie-breaker by multiplying the heuristic by (minimum cost)/(max possible path length)
        return heuristic
    if choice == 3:  # octile
        dx = abs(int(startx) - int(goalx))
        dy = abs(int(starty) - int(goaly))
        heuristic = (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)
        heuristic *= (
            1.0 + (0.25 / 160))  # tie-breaker by multiplying the heuristic by (minimum cost)/(max possible path length)
        return heuristic
    if choice == 4:  # Chebyshev
        heuristic = max(abs(startx - goalx), abs(starty - goaly))
        heuristic *= (1.0 + (0.25 / 160))
        return heuristic
    return 0


class AStarSearch(object):
    def findPath(self, startx, starty, goalx, goaly, choice):
        fringe = Queue()
        expanded_list = {}
        cost_added = {}
        start = Point(startx, starty, None)
        final_path = []
        fringe.put(start, 0)
        goal = (goalx, goaly)
        h_values = {}
        pList = {}
        expanded_list[(start.get_x(), start.get_y())] = None
        cost_added[(start.get_x(), start.get_y())] = 0

        while not fringe.empty():
            current = fringe.get()
            if (current.get_x(), current.get_y()) == goal:
                cellPointer = current
                while cellPointer != None:
                    final_path.append((cellPointer.get_x(), cellPointer.get_y()))
                    cellPointer = cellPointer.get_parent()
                break

            for next in get_neighbors(current.get_x(), current.get_y()):
                new_cost = cost_added[(current.get_x(), current.get_y())] + get_cost(current.get_x(), current.get_y(),
                                                                                     next[0], next[1])
                if next not in cost_added or new_cost < cost_added[next]:
                    cost_added[next] = new_cost  # g
                    next_heuristic = self.heuristic(next[0], next[1], goal_x, goal_y, choice)
                    priority = new_cost + next_heuristic
                    h_values[next] = next_heuristic
                    pList[next] = priority
                    fringe.put(Point(next[0], next[1], current), priority)
                    expanded_list[next] = current

        return expanded_list, cost_added, final_path, cost_added[(goalx, goaly)], pList, h_values

    def heuristic(self, startx, starty, goalx, goaly, type):
        start = (startx, starty)
        goal = (goalx, goaly)
        type = int(type)

        if type == 1:  # manhattan
            heuristic = abs(int(startx) - int(goalx)) + abs(int(starty) - int(goaly))
            heuristic *= (
                1.0 + (
                    0.25 / 160))
            return heuristic
        if type == 2:  # euclidean
            heuristic = math.sqrt(((int(startx) - int(goalx)) ** 2) + ((int(starty) - int(goaly)) ** 2))
            heuristic *= (
                1.0 + (
                    0.25 / 160))
            return heuristic
        if type == 3:  # octile
            dx = abs(int(startx) - int(goalx))
            dy = abs(int(starty) - int(goaly))
            heuristic = (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)
            heuristic *= (
                1.0 + (
                    0.25 / 160))
            return heuristic
        if type == 4:  # Chebyshev
            heuristic = max(abs(startx - goalx), abs(starty - goaly))
            heuristic *= (1.0 + (0.25 / 160))
            return heuristic
        return 0


class UniformCostSearch(AStarSearch):
    def heuristic(self, startx, starty, goalx, goaly, type):
        return 1


class WeightedAStarSearch(AStarSearch):
    def __init__(self, weight):
        self.weight = weight

    def heuristic(self, startx, starty, goalx, goaly, type):
        return super(WeightedAStarSearch, self).heuristic(startx, starty, goalx, goaly, type) * float(self.weight)

#TODO: finish sequential A*
class SequentialAStarSearch(AStarSearch):
    def findPath(self, startx, starty, goalx, goaly, notused):
        fringe = [Queue() for x in range(5)]
        start = Point(startx, starty, None)
        goal = (goalx, goaly)

        closed_list = [dict() for y in range(0, 5)]
        cost_added = [dict() for y in range(0, 5)]
        heuristic_list = [dict() for y in range(0, 5)]
        final_path = []
        priority_list = [dict() for y in range(0, 5)]
        w2 = 1  # weight
        path_cost = 0

        for i in range(0, 5):
            closed_list[i] = {}
            cost_added[i] = {}
            heuristic_list[i] = {}
            for next in get_neighbors(start.get_x(), start.get_y()):
                # print "current x %d current y %d" % current[0], current[1]
                new_cost = get_cost(start.get_x(), start.get_y(), next[0], next[1])
                if next not in cost_added[i] or new_cost < cost_added[i][next]:
                    # if next not in closed_list or new_cost < cost_added[next]:
                    cost_added[i][next] = new_cost  # g
                    myheuristic = self.heuristic(next[0], next[1], goal_x, goal_y, i + 1)
                    priority = new_cost + myheuristic
                    heuristic_list[i][next] = myheuristic
                    priority_list[i][next] = priority
                    fringe[i].put(Point(next[0], next[1], start), priority)
                    closed_list[i][next] = start
            closed_list[i][(start.get_x(), start.get_y())] = None
            cost_added[i][(start.get_x(), start.get_y())] = 0
            cost_added[i][(goalx, goaly)] = float("inf")


        while not fringe[0].empty():
            anchor = fringe[0].getFull()
            for i in range(1, 5):
                # anchor is a tuple (item, priority)
                temp = fringe[i].getFull()  # temp is a tuple (item, priority)

                if temp != -1 and temp[1] <= w2 * anchor[1]:  # main condition
                    if temp[0].get_x() == goalx and temp[0].get_y() == goaly:
                        path_cost = 0
                        # Make a straight path from goal to start
                        PathNode = temp[0]
                        old_x = PathNode.get_x()
                        old_y = PathNode.get_y()
                        final_path.append((old_x, old_y))
                        PathNode = PathNode.get_parent()

                        while PathNode != None:
                            path_cost += get_cost(PathNode.get_x(), PathNode.get_y(), old_x, old_y)
                            final_path.append((PathNode.get_x(), PathNode.get_y()))
                            # print "Path: " + str(current.get_x()) + "," + str(current.get_y())
                            old_x = PathNode.get_x()
                            old_y = PathNode.get_y()
                            PathNode = PathNode.get_parent()

                        # break
                        return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list
                    else:
                        # print "adding to fringe[" + str(i)+"]"
                        for next in get_neighbors(temp[0].get_x(), temp[0].get_y()):
                            # print "current x %d current y %d" % current[0], current[1]
                            new_cost = cost_added[i][(temp[0].get_x(), temp[0].get_y())] + get_cost(temp[0].get_x(),
                                                                                                    temp[0].get_y(),
                                                                                                    next[0], next[1])

                            if next not in cost_added[i] or new_cost < cost_added[i][next]:
                                # print "Added neighbor"
                                # if next not in closed_list or new_cost < cost_added[next]:
                                cost_added[i][next] = new_cost  # g
                                myheuristic = self.heuristic(next[0], next[1], goalx, goaly, i + 1)
                                priority = new_cost + myheuristic
                                heuristic_list[i][next] = myheuristic
                                priority_list[i][next] = priority
                                fringe[i].put(Point(next[0], next[1], temp[0]), priority)
                                closed_list[i][next] = temp[0]

                else:
                    # print "------------- Reached the else condition, using fringe[0] ---------------"
                    if anchor[0].get_x() == goalx and anchor[0].get_y() == goaly:
                        # Found goal, return path
                        print "Made it to goal at " + str(goal[0]) + "," + str(goal[1])
                        path_cost = 0
                        # Make a straight path from goal to start
                        PathNode = anchor[0]
                        old_x = PathNode.get_x()
                        old_y = PathNode.get_y()
                        final_path.append((old_x, old_y))
                        PathNode = PathNode.get_parent()

                        while PathNode != None:
                            path_cost += get_cost(PathNode.get_x(), PathNode.get_y(), old_x, old_y)
                            final_path.append((PathNode.get_x(), PathNode.get_y()))
                            # print "Path: " + str(current.get_x()) + "," + str(current.get_y())
                            old_x = PathNode.get_x()
                            old_y = PathNode.get_y()
                            PathNode = PathNode.get_parent()

                        # break
                        return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list
                    else:
                        # print "-------------- adding to fringe[0] ---------------"
                        for next in get_neighbors(anchor[0].get_x(), anchor[0].get_y()):
                            # print "current x %d current y %d" % current[0], current[1]
                            new_cost = cost_added[0][(anchor[0].get_x(), anchor[0].get_y())] + get_cost(
                                anchor[0].get_x(),
                                anchor[0].get_y(),
                                next[0], next[1])

                            if next not in cost_added[0] or new_cost < cost_added[0][next]:
                                # print "Added neighbor"
                                # if next not in closed_list or new_cost < cost_added[next]:
                                cost_added[0][next] = new_cost  # g
                                myheuristic = self.heuristic(next[0], next[1], goalx, goaly, 1)
                                priority = new_cost + myheuristic
                                heuristic_list[0][next] = myheuristic
                                priority_list[0][next] = priority
                                fringe[0].put(Point(next[0], next[1], anchor[0]), priority)
                                closed_list[0][next] = anchor[0]

        return closed_list, cost_added, final_path, path_cost, priority_list, heuristic_list

    def heuristic(self, startx, starty, goalx, goaly, type):
        super(SequentialAStarSearch, self).heuristic(startx, starty, goalx, goaly, type)


# Draw and fill cells

def draw(surf):
    surf.fill((255, 255, 255))
    for x in range(len(graph)):
        for y in range(len(graph[x])):
            if graph[x][y] == 'blocked':
                pygame.draw.rect(surf, (40, 40, 40),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE, TILESIZE), 0)
                pygame.draw.rect(surf, (40, 40, 40),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE + 1, TILESIZE + 1), 1)
            elif graph[x][y] == 'hard_traverse':
                pygame.draw.rect(surf, (200, 200, 200),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE, TILESIZE), 0)
                pygame.draw.rect(surf, (100, 100, 100),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE + 1, TILESIZE + 1), 1)
            elif graph[x][y] == 'blocked_highway':
                pygame.draw.rect(surf, (70, 90, 220),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE, TILESIZE), 0)
                pygame.draw.rect(surf, (100, 100, 100),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE + 1, TILESIZE + 1), 1)
            elif graph[x][y] == 'open':
                pygame.draw.rect(surf, (255, 255, 255),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE, TILESIZE), 0)
                pygame.draw.rect(surf, (100, 100, 100),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE + 1, TILESIZE + 1), 1)
            elif graph[x][y] == 'highway':
                pygame.draw.rect(surf, (130, 170, 255),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE, TILESIZE), 0)
                pygame.draw.rect(surf, (100, 100, 100),
                                 (x * TILESIZE + 10, y * TILESIZE + 10, TILESIZE + 1, TILESIZE + 1), 1)

    surf = surf.convert()
    return surf


# Draw UI


def draw_ui(GridSurface, closed_list, path, pathcost, nodes_expanded, elapsedtime, fn_g, fn_f, fn_h, mapcount):
    DISPLAYSURF.blit(GridSurface, (0, 0))

    pygame.draw.circle(DISPLAYSURF, (255, 0, 0),
                       (start_x * TILESIZE + TILESIZE / 2 + 10, start_y * TILESIZE + TILESIZE / 2 + 10),
                       TILESIZE / 2, 0)
    pygame.draw.circle(DISPLAYSURF, (0, 0, 255),
                       (goal_x * TILESIZE + TILESIZE / 2 + 10, goal_y * TILESIZE + TILESIZE / 2 + 10),
                       TILESIZE / 2, 0)

    pygame.draw.rect(DISPLAYSURF, (0, 255, 0),
                     (pointer_x * TILESIZE + 9, pointer_y * TILESIZE + 9, TILESIZE + 2, TILESIZE + 2), 2)

    # Draw text
    label = font.render(
        "N = Next Map / Endpoints | U = Uniform Cost Search | A = A* Search | W = Weighted A* | S = Save | L = Load",
        1, (0, 0, 0))
    DISPLAYSURF.blit(label, (20, TILESIZE * NUM_ROW + 14))

    label = font.render("Map " + str(mapcount/10) + ", Endpoints " + str(mapcount % 10), 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 30))

    label = font.render("Cell Pointer: (" + str(pointer_x) + "," + str(pointer_y) + ")", 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 60))

    label = font.render("Status: " + graph[pointer_x][pointer_y], 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 80))

    label = font.render("Start point: (" + str(start_x) + "," + str(start_y) + ")", 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 110))
    label = font.render("Goal point: (" + str(goal_x) + "," + str(goal_y) + ")", 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 130))

    if pathcost != 0:
        label = font.render("Trip Cost:", 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 160))
        label = font.render(str(pathcost), 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 180))

    if pathcost != 0:
        label = font.render("Grid Cells Expanded:", 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 200))
        label = font.render(str(nodes_expanded), 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 220))

    if (pointer_x, pointer_y) in fn_f:
        label = font.render("f: " + str(fn_f[(pointer_x, pointer_y)]), 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 250))

    if (pointer_x, pointer_y) in fn_g:
        label = font.render("g: " + str(fn_g[(pointer_x, pointer_y)]), 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 270))

    if (pointer_x, pointer_y) in fn_h:
        label = font.render("h: " + str(fn_h[(pointer_x, pointer_y)]), 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 290))

    label = font.render("Time: ", 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 320))
    label = font.render(str(elapsedtime * 1000) + " ms", 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 340))

    label = font.render("Neighbors:", 1, (0, 0, 0))
    DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, 370))

    draw_y = 390
    neighbors = get_neighbors(pointer_x, pointer_y)

    for neighbor in neighbors:
        label = font.render("(" + str(neighbor[0]) + "," + str(neighbor[1]) + ")", 1, (0, 0, 0))
        DISPLAYSURF.blit(label, (10 + TILESIZE * NUM_COL + 30, draw_y))
        draw_y += 20

    for cell in path:
        pygame.draw.circle(DISPLAYSURF, (255, 0, 0),
                           (cell[0] * TILESIZE + TILESIZE / 2 + 10, cell[1] * TILESIZE + TILESIZE / 2 + 10),
                           TILESIZE / 4, 0)

    pygame.display.update()

def terminate():
    pygame.quit()
    sys.exit()

# Main process
running = True

GridSurface = pygame.Surface(DISPLAYSURF.get_size())

hard_traverse_nodes = generateGraph()
GridSurface = draw(GridSurface)
start_x, start_y, goal_x, goal_y = generate_endpoints()
found_path = []
closed_list = []
cell_costs = []
pList = []
h_values = []
path_cost = 0
timer = 0
cells_checked = 0

search = AStarSearch()  # Initialize Object

mapcount = 0

while (running):
    # Get Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                terminate()
            elif event.key == pygame.K_n:
                #Next map and endpoints
                if (mapcount % 10) == 0 and mapcount != 0:
                    graph = [['open' for y in range(NUM_ROW)] for x in range(NUM_COL)]
                    hard_traverse_nodes = generateGraph()
                    GridSurface = draw(GridSurface)
                    start_x, start_y, goal_x, goal_y = generate_endpoints()
                    found_path = []
                    closed_list = []
                    pList = []
                    h_values = []
                    cell_costs = []
                    path_cost = 0
                    timer = 0
                    cells_checked = 0
                    if mapcount == 50:
                        mapcount = 0
                    else:
                        mapcount += 1
                else:
                    start_x, start_y, goal_x, goal_y = generate_endpoints()
                    found_path = []
                    closed_list = []
                    pList = []
                    h_values = []
                    cell_costs = []
                    path_cost = 0
                    timer = 0
                    cells_checked = 0
                    if mapcount == 50:
                        mapcount = 0
                    else:
                        mapcount += 1

            elif event.key == pygame.K_s:
                # Save map: get filename
                filename = raw_input("Save map to: ")
                with open(os.path.join("./maps", filename), "w") as mapfile:
                    mapfile.write(str((start_x, start_y)))
                    mapfile.write("\n")
                    mapfile.write(str((goal_x, goal_y)))
                    mapfile.write("\n")
                    for area in hard_traverse_nodes:
                        mapfile.write(str((area[0], area[1])))
                        mapfile.write("\n")
                    for y in range(len(graph[x])):
                        for x in range(len(graph)):
                            mapfile.write(str(graph[x][y]))
                        mapfile.write("\n")
                    mapfile.close()

            elif event.key == pygame.K_l:

                filename = raw_input("Load map from: ")
                with open(os.path.join("./maps", filename), "r") as mapfile:  # changed to allow using /maps folder
                    new_start = make_tuple(mapfile.readline())
                    start_x = new_start[0]
                    start_y = new_start[1]
                    new_goal = make_tuple(mapfile.readline())
                    goal_x = new_goal[0]
                    goal_y = new_goal[1]
                    hard_traverse_nodes = []
                    for i in range(8):
                        new_area = make_tuple(mapfile.readline())
                        hard_traverse_nodes.append((new_area[0], new_area[1]))
                    for y in range(len(graph[x])):
                        for x in range(len(graph)):
                            graph[x][y] = mapfile.read(1)
                        mapfile.read(1)
                    mapfile.close()

                found_path = []
                closed_list = []
                cell_costs = []
                pList = []
                h_values = []
                path_cost = 0
                timer = 0
                cells_checked = 0
                GridSurface = draw(GridSurface)
            elif event.key == pygame.K_UP:
                if pointer_y - 1 >= 0:
                    pointer_y -= 1
            elif event.key == pygame.K_LEFT:
                if pointer_x - 1 >= 0:
                    pointer_x -= 1
            elif event.key == pygame.K_RIGHT:
                if pointer_x + 1 < NUM_COL:
                    pointer_x += 1
            elif event.key == pygame.K_DOWN:
                if pointer_y + 1 < NUM_ROW:
                    pointer_y += 1
            elif event.key == pygame.K_a:
                hType = 4
                search = AStarSearch()
                start_time = time.time()
                closed_list, cell_costs, found_path, path_cost, pList, h_values = search.findPath(
                    start_x,
                    start_y,
                    goal_x,
                    goal_y,
                    hType)
                timer = time.time() - start_time
                cells_checked = len(closed_list)

            elif event.key == pygame.K_u:
                search = UniformCostSearch()
                start_time = time.time()
                closed_list, cell_costs, found_path, path_cost, pList, h_values = search.findPath(
                    start_x,
                    start_y,
                    goal_x,
                    goal_y,
                    1)
                timer = time.time() - start_time
                cells_checked = len(closed_list)

            elif event.key == pygame.K_w: #weighted A*
                hType = 3
                weight = 0

                while float(weight) < 1:
                    weight = raw_input("Enter a weight for your search: ")

                search = WeightedAStarSearch(weight)
                start_time = time.time()
                closed_list, cell_costs, found_path, path_cost, pList, h_values = search.findPath(
                    start_x,
                    start_y,
                    goal_x,
                    goal_y,
                    hType)
                timer = time.time() - start_time

                cells_checked = len(closed_list)
            elif event.key == pygame.K_q:
                search = AStarSearch()

        draw_ui(GridSurface, closed_list, found_path, path_cost, cells_checked, timer, cell_costs,
                pList, h_values, mapcount)

pygame.quit()
